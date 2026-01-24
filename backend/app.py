"""
Aplicación Flask para QuimicAI.
"""
import logging
import sys
import os

from flask import Flask
from flask_cors import CORS

# Agregar el directorio raíz al path para imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.core.config import AppConfig
from backend.core.assistant import ChemicalAssistant
from backend.api.routes import api_bp, init_routes

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app(config: AppConfig = None) -> Flask:
    """
    Application factory para crear la app Flask.
    
    Args:
        config: Configuración de la aplicación. Si no se provee, usa AppConfig por defecto.
    
    Returns:
        Aplicación Flask configurada
    """
    if config is None:
        config = AppConfig()
    
    # Validar configuración
    try:
        config.validate()
    except Exception as e:
        logger.error(f"Error en la configuración: {e}")
        raise
    
    # Crear aplicación Flask
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    template_folder = os.path.join(project_root, 'frontend', 'templates')
    static_folder = os.path.join(project_root, 'frontend', 'static')
    
    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)
    
    # Configurar CORS
    CORS(app)
    
    # Inicializar el asistente químico
    logger.info("Inicializando Chemical Assistant...")
    assistant = ChemicalAssistant(config)
    
    # Inicializar rutas con el asistente
    init_routes(assistant)
    
    # Registrar blueprints
    app.register_blueprint(api_bp)
    
    # Ruta principal para servir el frontend
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    logger.info("✅ Aplicación Flask inicializada correctamente")
    
    return app
