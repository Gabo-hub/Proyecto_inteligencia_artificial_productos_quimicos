"""
API routes para el asistente químico.
"""
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

# Crear blueprint para las rutas de API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Variable global para el asistente (se inicializará desde app.py)
assistant = None


def init_routes(chemical_assistant):
    """Inicializa las rutas con la instancia del asistente."""
    global assistant
    assistant = chemical_assistant
    logger.info("Rutas API inicializadas correctamente")


@api_bp.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint para hacer preguntas al asistente.
    
    Request JSON:
        {
            "question": "¿Qué es el vinagre blanco?"
        }
    
    Response JSON:
        {
            "answer": "...",
            "sources": [...]
        }
    """
    if not assistant:
        logger.error("El asistente no está inicializado")
        return jsonify({"error": "El asistente no está disponible"}), 500
    
    data = request.get_json()
    query = data.get("question", "")
    
    if not query:
        return jsonify({"error": "No se envió ninguna pregunta"}), 400
    
    try:
        logger.info(f"Procesando pregunta: {query}")
        respuesta, fuentes = assistant.ask(query)
        
        return jsonify({
            "answer": respuesta,
            "sources": [f.metadata for f in fuentes] if fuentes else []
        })
    
    except Exception as e:
        logger.error(f"Error al procesar pregunta: {e}", exc_info=True)
        return jsonify({"error": "Error al procesar la pregunta"}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """Endpoint de health check."""
    return jsonify({
        "status": "ok",
        "assistant_ready": assistant is not None
    })
