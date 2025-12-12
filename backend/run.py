"""
Entry point para correr el servidor Flask.
"""
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz del proyecto al path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Cargar variables de entorno
load_dotenv()

from app import create_app
from core.config import AppConfig

if __name__ == "__main__":
    # Crear configuración
    config = AppConfig()
    
    # Crear y correr la aplicación
    app = create_app(config)
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
