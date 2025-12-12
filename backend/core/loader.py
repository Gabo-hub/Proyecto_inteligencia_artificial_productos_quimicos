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
        
        # 1. Inventario Químico
        for item in datos.get("inventario_quimico", []):
            texto = KnowledgeLoader._format_chemical_item(item)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "inventario", "id": item.get("id")}
            ))

        # 2. Recetas Sugeridas
        for receta in datos.get("recetas_sugeridas", []):
            texto = KnowledgeLoader._format_recipe_item(receta)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "receta", "nombre": receta.get("nombre")}
            ))

        # 3. Reglas Prohibidas
        for regla in datos.get("reglas_prohibidas_guardrails", []):
            texto = KnowledgeLoader._format_rule_item(regla)
            documentos.append(Document(
                page_content=texto, 
                metadata={"source": "guardrail", "tipo": "seguridad"}
            ))

        logger.info(f"Cargados {len(documentos)} documentos de la base de conocimiento.")
        return documentos

    @staticmethod
    def _format_chemical_item(item: Dict[str, Any]) -> str:
        """Formatea un item químico como texto."""
        nombres = ", ".join(item.get("nombres", []))
        usos = ", ".join(item.get("usos_comunes", []))
        incompatibles = ", ".join(item.get("seguridad", {}).get("incompatible_con", []))
        return (
            f"Ingrediente: {nombres}\n"
            f"Categoría: {item.get('categoria', 'General')}\n"
            f"Descripción: {item.get('descripcion', '')}\n"
            f"pH: {item.get('ph', 'Desconocido')}\n"
            f"Toxicidad: {item.get('seguridad', {}).get('toxicidad', 'Desconocida')}\n"
            f"Incompatible con: {incompatibles}\n"
            f"Usos comunes: {usos}"
        )

    @staticmethod
    def _format_recipe_item(receta: Dict[str, Any]) -> str:
        """Formatea una receta como texto."""
        ingredientes_lista = ", ".join([
            f"{ing.get('cantidad', '?')} de {ing.get('id', '?')}" 
            for ing in receta.get("ingredientes", [])
        ])
        return (
            f"Receta: {receta.get('nombre', 'Sin nombre')}\n"
            f"Categoría: {receta.get('categoria', 'General')}\n"
            f"Ingredientes necesarios: {ingredientes_lista}\n"
            f"Instrucciones: {receta.get('instrucciones', '')}\n"
            f"Advertencias: {receta.get('advertencias', '')}"
        )

    @staticmethod
    def _format_rule_item(regla: Dict[str, Any]) -> str:
        """Formatea una regla de seguridad como texto."""
        return (
            f"PELIGRO DE MEZCLA:\n"
            f"No mezclar {regla.get('ingrediente_A')} con {regla.get('ingrediente_B')}.\n"
            f"Resultado: {regla.get('resultado')}. Peligro: {regla.get('peligro')}\n"
            f"Advertencia: {regla.get('mensaje_usuario')}"
        )
