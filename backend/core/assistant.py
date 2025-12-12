"""
Asistente de IA para consultas sobre productos químicos.
"""
import os
import logging
from typing import List, Tuple, Optional

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import Runnable

from backend.core.config import AppConfig
from backend.core.loader import KnowledgeLoader

logger = logging.getLogger(__name__)


class ChemicalAssistant:
    """Clase principal que maneja el ciclo de vida del asistente IA."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.vector_db = None
        self.chain: Optional[Runnable] = None
        self._initialize()

    def _initialize(self):
        """Inicializa componentes pesados (Embeddings, Vector Store, LLM)."""
        logger.info("Inicializando componentes del sistema...")
        
        # Cargar documentos
        docs = KnowledgeLoader.load_from_json(self.config.DATA_FILE)
        if not docs:
            logger.warning("La base de datos está vacía o no se pudo cargar.")
        
        # Crear Embeddings y Vector Store
        logger.info(f"Cargando modelo de embeddings: {self.config.MODEL_NAME}")
        embeddings = OllamaEmbeddings(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL
        )
        
        # Intentar cargar vector store desde caché
        if docs:
            if os.path.exists(self.config.VECTOR_STORE_PATH):
                logger.info("Cargando vector store desde caché...")
                try:
                    self.vector_db = FAISS.load_local(
                        self.config.VECTOR_STORE_PATH, 
                        embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info("✅ Vector store cargado desde caché.")
                except Exception as e:
                    logger.warning(f"No se pudo cargar caché: {e}. Creando nuevo vector store...")
                    self.vector_db = None
            
            if not self.vector_db:
                logger.info(f"Creando vector store FAISS para {len(docs)} documentos...")
                logger.info("⏳ Esto puede tomar unos minutos la primera vez...")
                self.vector_db = FAISS.from_documents(docs, embeddings)
                
                # Guardar en caché
                logger.info("Guardando vector store en caché...")
                self.vector_db.save_local(self.config.VECTOR_STORE_PATH)
                logger.info("✅ Vector store creado y guardado en caché.")
            
            retriever = self.vector_db.as_retriever()
        else:
            self.vector_db = None
            retriever = None

        # Configurar LLM y Chain
        logger.info("Configurando LLM...")
        prompt = ChatPromptTemplate.from_template(self.config.SYSTEM_PROMPT)
        llm = OllamaLLM(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            timeout=self.config.LLM_TIMEOUT
        )

        # Definir la cadena (chain)
        def retrieve_fn(query: str):
            if not retriever:
                return []
            return retriever.invoke(query)

        self.retriever = retrieve_fn
        self.llm_chain = prompt | llm
        
        logger.info("Sistema inicializado correctamente.")

    def ask(self, query: str) -> Tuple[str, List[Document]]:
        """Procesa una pregunta del usuario y devuelve respuesta + fuentes."""
        
        # 1. Retrieve
        relevant_docs = self.retriever(query)
        logger.info(f"Query: '{query}' -> {len(relevant_docs)} documentos recuperados")
        
        context_str = "\n\n".join([d.page_content for d in relevant_docs])
        
        if not context_str.strip():
            logger.warning(f"ATENCION: El contexto esta vacio para la query '{query}'")
        else:
            logger.info(f"Contexto generado: {len(context_str)} caracteres")
        
        # 2. Generate
        response = self.llm_chain.invoke({
            "context": context_str,
            "question": query
        })
        
        return response, relevant_docs
