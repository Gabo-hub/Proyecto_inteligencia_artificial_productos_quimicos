import csv
import json
import os

def normalize_name(name):
    """Normaliza nombres para comparación."""
    if not name: return ""
    return name.lower().strip()

def clean_cell(value):
    """
    Limpia un valor de celda.
    Maneja casos donde el valor es None, String o Lista (por columnas duplicadas).
    """
    if value is None:
        return ""
    if isinstance(value, list):
        # Si el CSV tiene cabeceras duplicadas, el valor es una lista.
        # Unimos los valores con espacio.
        return " ".join(str(v) for v in value).strip()
    return str(value).strip()

def build_json():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    json_path = os.path.join(DATA_DIR, "database.json")
    csv_recetas_path = os.path.join(DATA_DIR, "recetas.csv")
    csv_elementos_path = os.path.join(DATA_DIR, "elementos.csv")
    csv_train_path = os.path.join(DATA_DIR, "train.csv")
    csv_reglas_path = os.path.join(DATA_DIR, "reglas_seguridad.csv")
    
    # 1. Cargar JSON actual
    print("Cargando database.json actual...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró database.json.")
        return

    # 2. Mapa de Nombres -> IDs
    name_to_id = {}
    for item in data.get("inventario_quimico", []):
        for name in item.get("nombres", []):
            name_to_id[normalize_name(name)] = item.get("id")
        name_to_id[item.get("id").lower()] = item.get("id")
        
    manual_map = {
        "agua": "ing_015",
        "h2o": "ing_015",
        "jabon neutro": "ing_009",
        "esencia de lavanda": "ing_017"
    }
    name_to_id.update(manual_map)

    def get_ingredient_id(name_str):
        clean_name = normalize_name(name_str)
        if clean_name in name_to_id:
            return name_to_id[clean_name]
        for key, val in name_to_id.items():
            if key in clean_name or clean_name in key:
                return val
        return None

    # 3. Procesar REGLAS
    print("Procesando reglas de seguridad...")
    new_reglas = set() 
    for r in data.get("reglas_prohibidas_guardrails", []):
        new_reglas.add(json.dumps(r, sort_keys=True))

    if os.path.exists(csv_reglas_path):
        with open(csv_reglas_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                if row is None: continue
                # USAMOS clean_cell para manejar listas y Nones
                row = { clean_cell(k): clean_cell(v) for k, v in row.items() }
                
                rule = {
                    "ingrediente_A": row.get("Ingrediente_A", ""),
                    "ingrediente_B": row.get("Ingrediente_B", ""),
                    "resultado": row.get("Resultado", ""),
                    "peligro": row.get("Peligro", ""),
                    "mensaje_usuario": row.get("Mensaje_Usuario", "")
                }
                if rule["ingrediente_A"] and rule["ingrediente_B"]:
                    new_reglas.add(json.dumps(rule, sort_keys=True))
    
    data["reglas_prohibidas_guardrails"] = [json.loads(r) for r in new_reglas]

    # 4. Procesar RECETAS
    print("Procesando recetas.csv...")
    existing_recipes_ids = {r["id_receta"] for r in data.get("recetas_sugeridas", [])}
    
    if os.path.exists(csv_recetas_path):
        with open(csv_recetas_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                if row is None: continue
                # USAMOS clean_cell
                row = { clean_cell(k): clean_cell(v) for k, v in row.items() }

                rid = row.get("ID_Receta", "")
                
                if rid and rid not in existing_recipes_ids:
                    ingredientes_list = []
                    ings_raw = row.get("Ingredientes", "").split('|')
                    for ing_part in ings_raw:
                        if ':' in ing_part:
                            iid, qty = ing_part.split(':', 1)
                            ingredientes_list.append({
                                "id": iid.strip(),
                                "cantidad": qty.strip()
                            })
                    
                    recipe = {
                        "id_receta": rid,
                        "nombre": row.get("Nombre", ""),
                        "categoria": row.get("Categoria", ""),
                        "ingredientes": ingredientes_list,
                        "instrucciones": row.get("Instrucciones", ""),
                        "advertencias": row.get("Advertencias", "")
                    }
                    data["recetas_sugeridas"].append(recipe)

    # 5. Procesar PRODUCTOS (Elementos y Train)
    def process_product_csv(filepath, prefix_id):
        if not os.path.exists(filepath): return []
        new_items = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            for idx, row in enumerate(reader):
                if row is None: continue
                # USAMOS clean_cell
                row = { clean_cell(k): clean_cell(v) for k, v in row.items() }

                ingredientes_list = []
                ings_raw = row.get("Ingredientes disponibles", "").split(',')
                for ing in ings_raw:
                    clean_ing = ing.strip()
                    ing_id = get_ingredient_id(clean_ing)
                    if ing_id:
                        ingredientes_list.append({"id": ing_id, "cantidad": "Al gusto"})
                    else:
                        ingredientes_list.append({"id": clean_ing, "cantidad": "Al gusto"})

                csv_id = row.get("ID", "")
                rec_id = csv_id if csv_id else f"{prefix_id}_{idx+1:03d}"
                
                if any(r['id_receta'] == rec_id for r in data["recetas_sugeridas"]):
                    rec_id = f"{prefix_id}_ext_{idx+1:03d}"

                item = {
                    "id_receta": rec_id,
                    "nombre": row.get("Producto", "Sin nombre"),
                    "categoria": row.get("Propósito", "General"),
                    "ingredientes": ingredientes_list,
                    "instrucciones": row.get("Sugerencia de formulación", ""),
                    "advertencias": row.get("Restricciones", ""),
                    "combinaciones_clave": f"Basado en: {row.get('Propiedades deseadas', '')}"
                }
                new_items.append(item)
        return new_items

    print("Procesando elementos.csv y train.csv...")
    data["recetas_sugeridas"].extend(process_product_csv(csv_elementos_path, "elem"))
    data["recetas_sugeridas"].extend(process_product_csv(csv_train_path, "train"))

    # 6. Guardar
    print("Guardando database_actualizado.json...")
    output_path = os.path.join(DATA_DIR, "database_actualizado.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"¡Éxito! Archivo generado en: {output_path}")
    print(f"Total recetas: {len(data['recetas_sugeridas'])}")
    print("Por favor, renombra 'database_actualizado.json' a 'database.json' y borra la carpeta 'vector_store'.")

if __name__ == "__main__":
    build_json()