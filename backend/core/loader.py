"""
Cargador de base de conocimientos desde archivos JSON.
Versión mejorada: normalización, deduplicación, metadatos de fuente y parsing robusto.
"""
import json
import os
import logging
import re
from typing import List, Dict, Any

from langchain_core.documents import Document

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _norm(s: str) -> str:
    if not s:
        return ""
    return str(s).strip().lower()

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

        documentos: List[Document] = []

        # Inventario
        inventory_items = datos.get("inventario_quimico", [])
        # Deduplicar por id (mantener la primera aparición)
        seen_ids = set()
        dedup_inventory = []
        for item in inventory_items:
            iid = item.get("id")
            if not iid:
                logger.warning("Item sin id en inventario, se omite: %s", item)
                continue
            if iid in seen_ids:
                logger.warning("ID duplicado en inventario detectado y omitido: %s", iid)
                continue
            seen_ids.add(iid)
            dedup_inventory.append(item)
        inventory_items = dedup_inventory

        # Construir mapas: id -> primary name, name(normalizado) -> id
        id_to_name: Dict[str, str] = {}
        name_to_id: Dict[str, str] = {}
        for item in inventory_items:
            iid = item.get("id")
            nombres = item.get("nombres", [])
            primary_name = nombres[0] if nombres else iid
            id_to_name[iid] = primary_name
            # registrar todos los sinónimos normalizados
            for n in nombres:
                key = _norm(n)
                if key:
                    name_to_id[key] = iid
            # también indexar el id textual
            name_to_id[_norm(iid)] = iid

        # Añadir manual_map si existe en datos.meta_info (opcional)
        manual_map = datos.get("manual_name_map", {})
        for k, v in manual_map.items():
            name_to_id[_norm(k)] = v

        def resolve_name_to_id(name_str: str) -> str:
            """Resuelve un nombre a un id usando coincidencia exacta de tokens primero."""
            if not name_str:
                return None
            key = _norm(name_str)
            if key in name_to_id:
                return name_to_id[key]
            # token exact match: dividir en palabras y buscar coincidencia por palabra completa
            tokens = re.findall(r"\w+", key)
            for t in tokens:
                if t in name_to_id:
                    return name_to_id[t]
            # fallback: substring match (menos preferible)
            for k, v in name_to_id.items():
                if k in key or key in k:
                    return v
            return None

        # 1. Inventario Químico -> Documentos
        for item in inventory_items:
            texto = KnowledgeLoader._format_chemical_item(item, id_to_name)
            metadata = {
                "source": "inventario",
                "id": item.get("id"),
                "file": os.path.basename(file_path)
            }
            documentos.append(Document(page_content=texto, metadata=metadata))

        # 2. Recetas Sugeridas
        recetas = datos.get("recetas_sugeridas", [])
        for receta in recetas:
            texto = KnowledgeLoader._format_recipe_item(receta, id_to_name)
            # intentar extraer source si existe en receta
            source_meta = receta.get("source", {})
            metadata = {
                "source": "receta",
                "nombre": receta.get("nombre"),
                "file": source_meta.get("file", os.path.basename(file_path)),
                "row_id": source_meta.get("row_id", receta.get("id_receta"))
            }
            documentos.append(Document(page_content=texto, metadata=metadata))

        # 3. Reglas Prohibidas
        reglas = datos.get("reglas_prohibidas_guardrails", [])
        for regla in reglas:
            texto = KnowledgeLoader._format_rule_item(regla, id_to_name)
            metadata = {
                "source": "guardrail",
                "tipo": "seguridad",
                "file": regla.get("source", {}).get("file", os.path.basename(file_path))
            }
            documentos.append(Document(page_content=texto, metadata=metadata))

        logger.info(f"Cargados {len(documentos)} documentos de la base de conocimiento.")
        return documentos

    @staticmethod
    def _format_chemical_item(item: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea un item químico como texto (sin añadir información que no exista)."""
        id_map = id_map or {}
        nombres = ", ".join(item.get("nombres", []))
        usos = ", ".join(item.get("usos_comunes", []))

        # Resolve incompatibles names robustamente
        raw_incompatibles = item.get("seguridad", {}).get("incompatible_con", []) or []
        resolved_incompatibles = []
        for inc in raw_incompatibles:
            # inc puede ser "ing_001 (razón)" o "ing_001" o "Nombre común"
            inc_text = str(inc).strip()
            # extraer id entre ing_xxx con regex
            m = re.search(r"(ing_[0-9]+)", inc_text, flags=re.IGNORECASE)
            if m:
                ing_id = m.group(1)
                extra = ""
                # conservar el texto entre paréntesis si existe
                paren = re.search(r"\((.*)\)", inc_text)
                if paren:
                    extra = f" ({paren.group(1)})"
                ing_name = id_map.get(ing_id, ing_id)
                resolved_incompatibles.append(f"{ing_name}{extra}")
            else:
                # si no hay id, intentar resolver por nombre
                resolved_incompatibles.append(inc_text)

        incompatibles = ", ".join(resolved_incompatibles) if resolved_incompatibles else "[no especificado]"

        # Campos opcionales
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
            if isinstance(mascotas, dict):
                pets_warn = ", ".join([f"{k}: {v}" for k, v in mascotas.items()])
            else:
                pets_warn = str(mascotas)
            info_extra += f"⚠️ TOXICIDAD MASCOTAS: {pets_warn}\n"

        ph = item.get("ph", "Desconocido")
        rango_ph = item.get("rango_ph_preciso", "")

        return (
            f"Ingrediente: {nombres}\n"
            f"Categoría: {item.get('categoria', 'General')}\n"
            f"Descripción: {item.get('descripcion', '')}\n"
            f"{info_extra}"
            f"pH: {ph} {('('+rango_ph+')') if rango_ph else ''}\n"
            f"Toxicidad: {item.get('seguridad', {}).get('toxicidad', 'Desconocida')}\n"
            f"Incompatible con: {incompatibles}\n"
            f"Usos comunes: {usos}"
        )

    @staticmethod
    def _format_recipe_item(receta: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea una receta como texto. No inventa cantidades ni pasos que no existan."""
        id_map = id_map or {}
        ingredientes_lista = []
        for ing in receta.get("ingredientes", []):
            # soporta formatos {"id": "...", "cantidad": "..."} o strings
            if isinstance(ing, dict):
                ing_id = ing.get('id') or ing.get('chem_id') or ""
                nombre = id_map.get(ing_id, ing_id) if ing_id else ing.get("nombre", ing_id)
                cantidad = ing.get('cantidad', '')
                ingredientes_lista.append(f"{cantidad} de {nombre}".strip())
            else:
                # si es string, intentar parsear "ing_001: 1 taza" o "Bicarbonato de Sodio"
                text = str(ing).strip()
                if ':' in text:
                    left, right = text.split(':', 1)
                    ing_id = left.strip()
                    nombre = id_map.get(ing_id, ing_id)
                    ingredientes_lista.append(f"{right.strip()} de {nombre}")
                else:
                    ingredientes_lista.append(text)

        ingredientes_str = ", ".join(ingredientes_lista) if ingredientes_lista else "[no especificado]"

        instrucciones = receta.get('instrucciones', '') or receta.get('procedimiento', '') or ''
        advertencias = receta.get('advertencias', '') or receta.get('notas_seguridad', '') or ''

        # incluir source textual si existe
        source = receta.get("source", {})
        source_text = ""
        if source:
            source_text = f"\nFuente: {source.get('file', '')} {source.get('row_id', '')}".strip()

        return (
            f"Receta: {receta.get('nombre', 'Sin nombre')}\n"
            f"Categoría: {receta.get('categoria', 'General')}\n"
            f"Ingredientes necesarios: {ingredientes_str}\n"
            f"Instrucciones: {instrucciones}\n"
            f"Advertencias: {advertencias}{source_text}"
        )

    @staticmethod
    def _format_rule_item(regla: Dict[str, Any], id_map: Dict[str, str] = None) -> str:
        """Formatea una regla de seguridad como texto. Mantiene el mensaje original."""
        id_map = id_map or {}

        if "reactivos" in regla and isinstance(regla["reactivos"], list):
            participantes = " + ".join([id_map.get(r, r) for r in regla["reactivos"]])
        else:
            a = regla.get('ingrediente_A') or regla.get('reactivo_a') or ''
            b = regla.get('ingrediente_B') or regla.get('reactivo_b') or ''
            nome_a = id_map.get(a, a)
            nome_b = id_map.get(b, b)
            participantes = f"{nome_a} + {nome_b}"

        # Mantener el mensaje de usuario tal cual para seguridad
        mensaje = regla.get('mensaje_usuario') or regla.get('mensaje_alerta') or regla.get('mensaje', '')

        return (
            f"REGLA DE SEGURIDAD CRÍTICA:\n"
            f"Pregunta: ¿Qué pasa si mezclo {participantes}?\n"
            f"Respuesta: ¡PELIGRO! No lo hagas.\n"
            f"Consecuencia: {regla.get('resultado', '[no especificado]')}.\n"
            f"Riesgos de Salud: {regla.get('peligro', '[no especificado]')}\n"
            f"Advertencia Oficial: {mensaje}"
        )
