"""
Cargador de base de conocimientos desde archivos JSON.
"""
import json
import os
import logging
from typing import List, Dict, Any

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """Encargado de cargar y procesar la base de conocimientos."""
    
    @staticmethod
    def load_from_json(file_path: str) -> List[Document]:
        """Carga datos desde JSON y los convierte a documentos LangChain."""
        if not os.path.exists(file_path):
            logger.error(f"No se encontró el archivo: {file_path}")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"El archivo {file_path} no es un JSON válido.")
            return []
            
        documentos = []
        
        # Mapa de IDs a nombres para enriquecer todo
        id_to_name = {}
        inventory_items = datos.get("inventario_quimico", [])

        # Paso 0: Construir mapa de nombres primero
        for item in inventory_items:
            nombres = item.get("nombres", [])
            primary_name = nombres[0] if nombres else item.get("id")
            id_to_name[item.get("id")] = primary_name

        # 1. Inventario Químico
        for item in inventory_items:
            texto = KnowledgeLoader._format_chemical_item(item, id_to_name)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "inventario", "id": item.get("id")}
            ))

        # 2. Recetas Sugeridas
        for receta in datos.get("recetas_sugeridas", []):
            texto = KnowledgeLoader._format_recipe_item(receta, id_to_name)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "receta", "nombre": receta.get("nombre")}
            ))

        # 3. Reglas Prohibidas
        for regla in datos.get("reglas_prohibidas_guardrails", []):
            texto = KnowledgeLoader._format_rule_item(regla, id_to_name)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "guardrail", "tipo": "seguridad"}
            ))

        logger.info(f"Cargados {len(documentos)} documentos de la base de conocimiento.")
        return documentos

    @staticmethod
    def _format_chemical_item(item: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea un item químico como texto."""
        id_map = id_map or {}
        nombres = ", ".join(item.get("nombres", []))
        usos = ", ".join(item.get("usos_comunes", []))
        
        # Resolve incompatibles names
        raw_incompatibles = item.get("seguridad", {}).get("incompatible_con", [])
        resolved_incompatibles = []
        for inc in raw_incompatibles:
            # Handle "ing_001 (reason)" format if present, or just "ing_001"
            parts = inc.split(" (", 1)
            ing_id = parts[0]
            extra = f" ({parts[1]}" if len(parts) > 1 else ""
            
            ing_name = id_map.get(ing_id, ing_id)
            resolved_incompatibles.append(f"{ing_name}{extra}")
            
        incompatibles = ", ".join(resolved_incompatibles)
        
        # New fields formatting
        info_extra = ""
        if item.get("formula_quimica"):
            info_extra += f"Fórmula: {item.get('formula_quimica')}\n"
        if item.get("nombre_iupac"):
            info_extra += f"IUPAC: {item.get('nombre_iupac')}\n"
        if item.get("cas_number"):
            info_extra += f"CAS: {item.get('cas_number')}\n"
        
        nfpa = item.get("nfpa_704", {})
        if nfpa:
            info_extra += f"NFPA 704: Salud {nfpa.get('health')}, Inflamabilidad {nfpa.get('flammability')}, Inestabilidad {nfpa.get('instability')}\n"

        advertencia = item.get("seguridad", {}).get("advertencia_critica")
        if advertencia:
            info_extra += f"⚠️ ADVERTENCIA CRÍTICA: {advertencia}\n"
            
        mascotas = item.get("toxicidad_mascotas")
        if mascotas:
            # Handles both string and dict formats if present
            if isinstance(mascotas, dict):
                 pets_warn = ", ".join([f"{k}: {v}" for k,v in mascotas.items()])
            else:
                 pets_warn = str(mascotas)
            info_extra += f"⚠️ TOXICIDAD MASCOTAS: {pets_warn}\n"

        return (
            f"Ingrediente: {nombres}\n"
            f"Categoría: {item.get('categoria', 'General')}\n"
            f"Descripción: {item.get('descripcion', '')}\n"
            f"{info_extra}"
            f"pH: {item.get('ph', 'Desconocido')} ({item.get('rango_ph_preciso', '')})\n"
            f"Toxicidad: {item.get('seguridad', {}).get('toxicidad', 'Desconocida')}\n"
            f"Incompatible con: {incompatibles}\n"
            f"Usos comunes: {usos}"
        )

    @staticmethod
    def _format_recipe_item(receta: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea una receta como texto."""
        id_map = id_map or {}
        ingredientes_lista = []
        for ing in receta.get("ingredientes", []):
            ing_id = ing.get('id') or ing.get('chem_id', '?')
            nombre = id_map.get(ing_id, ing_id)
            cantidad = ing.get('cantidad', '?')
            ingredientes_lista.append(f"{cantidad} de {nombre}")

        ingredientes_str = ", ".join(ingredientes_lista)
        
        return (
            f"Receta: {receta.get('nombre', 'Sin nombre')}\n"
            f"Categoría: {receta.get('categoria', 'General')}\n"
            f"Ingredientes necesarios: {ingredientes_str}\n"
            f"Instrucciones: {receta.get('instrucciones', '')}\n"
            f"Advertencias: {receta.get('advertencias', '') or receta.get('notas_seguridad', '')}"
        )

    @staticmethod
    def _format_rule_item(regla: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea una regla de seguridad como texto."""
        id_map = id_map or {}
        
        # Handle both old (ingrediente_A/B) and new (reactivos list) formats
        if "reactivos" in regla:
            # Resolve names for reactivos list
            participantes = " + ".join([id_map.get(r, r) for r in regla["reactivos"]])
        else:
            # Resolve names for A/B format
            nome_a = id_map.get(regla.get('ingrediente_A'), regla.get('ingrediente_A'))
            nome_b = id_map.get(regla.get('ingrediente_B'), regla.get('ingrediente_B'))
            participantes = f"{nome_a} + {nome_b}"
            
        # Semantic SEO: Structure as a QA to match user queries
        return (
            f"REGLA DE SEGURIDAD CRÍTICA:\n"
            f"Pregunta: ¿Qué pasa si mezclo {participantes}?\n"
            f"Respuesta: ¡PELIGRO! No lo hagas.\n"
            f"Consecuencia: Produce {regla.get('resultado')}.\n"
            f"Riesgos de Salud: {regla.get('peligro')}\n"
            f"Advertencia Oficial: {regla.get('mensaje_usuario') or regla.get('mensaje_alerta')}"
        )
