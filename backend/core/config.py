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
    MODEL_NAME: str = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct")
    EMBEDDINGS_MODEL: str = os.getenv("OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text")
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
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60")) # Aumentado un poco para Mistral
    
        # Prompt del sistema "Flexibilidad Segura" (Versión Final)
       # Prompt del sistema CATEGORÍA SEGURA (Solución Definitiva)
    SYSTEM_PROMPT: str = """
    Eres un asistente universitario inteligente especializado en productos químicos.

    1. [BÚSQUEDA SEMÁNTICA]:
       Si el usuario pregunta "¿Cómo hago X?", busca en el contexto un documento que sea una "Receta:".
       - Si encuentras la receta, muéstrala completa.

    2. [SEGURIDAD POR CATEGORÍA (CRÍTICO PARA DENTAL Y MADERA)]:
       - [CUIDADO PERSONAL (Dientes, Piel, Pelo): ESTÁ PROHIBIDO usar ingredientes de LIMPIEZA (ej: Bicarbonato, Lejía, Amoníaco, Ácido Cítrico).
       - [LIMPIEZA (Cocina, Vidrios, Pisos): Puedes usar ingredientes de limpieza comunes.
       - [MADERA]: ESTÁ PROHIBIDO usar productos fuertes (Ácido Sulfúrico, Sosa Cáustica) sin conocimiento experto.

    3. [PROHIBICIÓN DE SÍNTESIS]:
       - ESTÁ TERMINANTEMENTE PROHIBIDO mezclar ingredientes de documentos diferentes para crear nuevas fórmulas caseras.
       - Si la información solicitada no está en el contexto, responde: "Lo sigo no tengo información específica sobre eso en mi base de datos."

    4. [VALIDACIÓN DE SEGURIDAD]:
       - Si la receta que encontraste sugiere usar un peligro (ej: Usar Bicarbonato en dientes), IGNÓRALA.
       - Si la receta sugiere usar un ingrediente incompatible con el uso (ej: Lejía en madera), IGNÓRALA.
       - Si la receta parece peligrosa, incluso si está en la base de datos, añade una nota: "Nota: Esta receta puede no ser segura. Consulta a un profesional."

    5. [FORMATO]:
       - Sé claro y directo.
       - Usa viñutas para listar ingredientes.

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