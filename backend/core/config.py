"""
Configuración centralizada de la aplicación QuimicAI.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Configuración centralizada de la aplicación."""
    
    # Modelo de IA
    MODEL_NAME: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Rutas de archivos
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATA_FILE: str = os.path.join(DATA_DIR, "database.json")
    VECTOR_STORE_PATH: str = os.path.join(DATA_DIR, "vector_store")
    
    # Configuración del servidor
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # Timeouts
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    
    # Prompt del sistema
    SYSTEM_PROMPT: str = """
    Eres un asistente universitario inteligente especializado en productos químicos.
    
    INSTRUCCIONES:
    1. Si el usuario pregunta por un producto químico o ingrediente, proporciónale toda la información relevante que encuentres en el contexto.
    2. Si el usuario solo menciona el nombre de un producto (por ejemplo: "Vinagre Blanco"), interpreta que quiere saber sobre ese producto y proporciona su información completa.
    3. Si el usuario hace una pregunta específica, respóndela basándote en el contexto.
    4. Si NO encuentras información relevante en el contexto, di "No tengo información sobre eso en mi base de datos".
    5. Responde de manera clara, organizada y útil.
    
    Contexto:
    {context}
    
    Pregunta/consulta del usuario:
    {question}
    """
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que las rutas y configuraciones existan."""
        config = cls()
        
        if not os.path.exists(config.DATA_FILE):
            raise FileNotFoundError(f"No se encontró el archivo de datos: {config.DATA_FILE}")
        
        return True
