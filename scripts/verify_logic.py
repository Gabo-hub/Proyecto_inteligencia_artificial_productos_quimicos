import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = os.path.join(BASE_DIR, "..", "data", "database.json")

class Document:
    def __init__(self, page_content):
        self.page_content = page_content
    def __repr__(self):
        return f"Document(page_content={self.page_content[:50]}...)"

def cargar_base_conocimiento():
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        documentos = []
        
        # 1. Inventario Químico
        if "inventario_quimico" in datos:
            for item in datos["inventario_quimico"]:
                nombres = ", ".join(item.get("nombres", []))
                usos = ", ".join(item.get("usos_comunes", []))
                incompatibles = ", ".join(item.get("seguridad", {}).get("incompatible_con", []))
                
                texto = (
                    f"Ingrediente: {nombres}\n"
                    f"Categoría: {item.get('categoria', 'General')}\n"
                    f"Descripción: {item.get('descripcion', '')}\n"
                    f"pH: {item.get('ph', 'Desconocido')}\n"
                    f"Toxicidad: {item.get('seguridad', {}).get('toxicidad', 'Desconocida')}\n"
                    f"Incompatible con: {incompatibles}\n"
                    f"Usos comunes: {usos}"
                )
                documentos.append(Document(page_content=texto))

        # 2. Recetas Sugeridas
        if "recetas_sugeridas" in datos:
            for receta in datos["recetas_sugeridas"]:
                ingredientes_lista = ", ".join([f"{ing['cantidad']} de {ing['id']}" for ing in receta.get("ingredientes", [])])
                
                texto = (
                    f"Receta: {receta.get('nombre', 'Sin nombre')}\n"
                    f"Categoría: {receta.get('categoria', 'General')}\n"
                    f"Ingredientes necesarios: {ingredientes_lista}\n"
                    f"Instrucciones: {receta.get('instrucciones', '')}\n"
                    f"Advertencias: {receta.get('advertencias', '')}"
                )
                documentos.append(Document(page_content=texto))

        # 3. Reglas Prohibidas (Guardrails)
        if "reglas_prohibidas_guardrails" in datos:
            for regla in datos["reglas_prohibidas_guardrails"]:
                texto = (
                    f"PELIGRO DE MEZCLA:\n"
                    f"No mezclar {regla.get('ingrediente_A')} con {regla.get('ingrediente_B')}.\n"
                    f"Resultado: {regla.get('resultado')}. Peligro: {regla.get('peligro')}\n"
                    f"Advertencia: {regla.get('mensaje_usuario')}"
                )
                documentos.append(Document(page_content=texto))

        return documentos
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {ARCHIVO_JSON}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo {ARCHIVO_JSON} no tiene un formato JSON válido.")
        return []

if __name__ == "__main__":
    docs = cargar_base_conocimiento()
    print(f"Total documents loaded: {len(docs)}")
    if len(docs) > 0:
        print("SAMPLE 1 (Ingredient):")
        print(docs[0].page_content)
        print("-" * 20)
        # Find a recipe
        for d in docs:
            if "Receta:" in d.page_content:
                print("SAMPLE 2 (Recipe):")
                print(d.page_content)
                break
