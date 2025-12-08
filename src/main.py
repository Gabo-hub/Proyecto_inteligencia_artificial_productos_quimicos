import json
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import Runnable

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Configuración centralizada de la aplicación."""
    MODEL_NAME: str = "llama3.2:3b"
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE: str = os.path.join(BASE_DIR, "..", "data", "database.json")
    
    # Prompt de contexto
    SYSTEM_PROMPT: str = """
    Eres un asistente universitario inteligente especializado en productos químicos.
    Responde a la pregunta basándote ÚNICAMENTE en el contexto proporcionado abajo.
    Si la respuesta no está en el contexto, di "No tengo información sobre eso en mi base de datos".
    
    Contexto:
    {context}
    
    Pregunta del usuario:
    {question}
    """

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
            documentos.append(Document(page_content=texto, metadata={"source": "inventario", "id": item.get("id")}))

        # 2. Recetas Sugeridas
        for receta in datos.get("recetas_sugeridas", []):
            texto = KnowledgeLoader._format_recipe_item(receta)
            documentos.append(Document(page_content=texto, metadata={"source": "receta", "nombre": receta.get("nombre")}))

        # 3. Reglas Prohibidas
        for regla in datos.get("reglas_prohibidas_guardrails", []):
            texto = KnowledgeLoader._format_rule_item(regla)
            documentos.append(Document(page_content=texto, metadata={"source": "guardrail", "tipo": "seguridad"}))

        logger.info(f"Cargados {len(documentos)} documentos de la base de conocimiento.")
        return documentos

    @staticmethod
    def _format_chemical_item(item: Dict[str, Any]) -> str:
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
        ingredientes_lista = ", ".join([f"{ing.get('cantidad', '?')} de {ing.get('id', '?')}" for ing in receta.get("ingredientes", [])])
        return (
            f"Receta: {receta.get('nombre', 'Sin nombre')}\n"
            f"Categoría: {receta.get('categoria', 'General')}\n"
            f"Ingredientes necesarios: {ingredientes_lista}\n"
            f"Instrucciones: {receta.get('instrucciones', '')}\n"
            f"Advertencias: {receta.get('advertencias', '')}"
        )

    @staticmethod
    def _format_rule_item(regla: Dict[str, Any]) -> str:
        return (
            f"PELIGRO DE MEZCLA:\n"
            f"No mezclar {regla.get('ingrediente_A')} con {regla.get('ingrediente_B')}.\n"
            f"Resultado: {regla.get('resultado')}. Peligro: {regla.get('peligro')}\n"
            f"Advertencia: {regla.get('mensaje_usuario')}"
        )

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
            # Continuamos, pero el retriever no devolverá nada útil
        
        # Crear Embeddings y Vector Store
        logger.info(f"Cargando modelo de embeddings: {self.config.MODEL_NAME}")
        embeddings = OllamaEmbeddings(model=self.config.MODEL_NAME)
        
        if docs:
            self.vector_db = FAISS.from_documents(docs, embeddings)
            retriever = self.vector_db.as_retriever()
        else:
            # Fallback simple si no hay docs para evitar crash inmediato
            self.vector_db = None
            retriever = None

        # Configurar LLM y Chain
        prompt = ChatPromptTemplate.from_template(self.config.SYSTEM_PROMPT)
        llm = OllamaLLM(model=self.config.MODEL_NAME)

        # Definir la cadena (chain)
        # Nota: Si retriever es None, esto fallará al ejecutarse si no lo manejamos,
        # pero mantenemos la estructura simple.
        
        def retrieve_fn(query: str):
            if not retriever:
                return []
            return retriever.invoke(query)

        # Custom chain logic to include retrieval
        self.retriever = retrieve_fn
        self.llm_chain = prompt | llm
        
        logger.info("Sistema inicializado correctamente.")

    def ask(self, query: str) -> Tuple[str, List[Document]]:
        """Procesa una pregunta del usuario y devuelve respuesta + fuentes."""
        
        # 1. Retrieve
        relevant_docs = self.retriever(query)
        context_str = "\n\n".join([d.page_content for d in relevant_docs])
        
        # 2. Generate
        response = self.llm_chain.invoke({
            "context": context_str,
            "question": query
        })
        
        return response, relevant_docs

def main():
    config = AppConfig()
    app = ChemicalAssistant(config)
    
    print(f"\n✅ Asistente listo (Modelo: {config.MODEL_NAME}). Escribe 'salir' para terminar.\n")
    
    while True:
        try:
            user_input = input(">> Tú: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("👋 ¡Hasta luego!")
                break
            
            print("⏳ Pensando...")
            respuesta, fuentes = app.ask(user_input)
            
            print(f"\n🤖 IA: {respuesta}")
            # Mostrar fuentes en modo debug si se desea
            # if fuentes:
            #    print(f"\n[Fuente principal: {fuentes[0].metadata}]")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Salida forzada.")
            break
        except Exception as e:
            logger.error(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()