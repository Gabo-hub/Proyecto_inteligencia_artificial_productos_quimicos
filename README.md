# Asistente para la formulacion de productos quimicos IA

# Pasos para la instalación:

1.  **Instalar Python:**
    Descarga e instala Python desde su sitio web oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2.  **Clonar el repositorio e instalar dependencias del proyecto:**
    Clona el repositorio en tu terminal y ejecuta el siguiente comando para instalar las librerías necesarias:
    ```bash
    git clone https://github.com/Gabo-hub/Proyecto_inteligencia_artificial_productos_quimicos.git
    cd Proyecto_inteligencia_artificial_productos_quimicos
    pip install -r requirements.txt
    ```

3.  **Descargar Ollama:**
    Obtén Ollama, la plataforma para ejecutar modelos de lenguaje localmente, desde su página oficial: [https://ollama.com/](https://ollama.com/)

4.  **Descargar el modelo `llama3.2:3b`:**
    Abre una terminal (PowerShell o CMD en Windows, o tu terminal preferida en Linux/macOS) y ejecuta el siguiente comando para descargar el modelo de lenguaje:
    ```bash
    ollama pull llama3.2:3b
    ```
    Espera a que la descarga se complete (verás una barra de progreso). Para verificar que el modelo se instaló correctamente, ejecuta:
    ```bash
    ollama list
    ```
    Deberías ver `llama3.2:3b` listado, similar a esto:
    ```
    NAME            ID              SIZE    MODIFIED
    llama3.2:3b     a1b2c3d4...     2.0GB   Just now
    ```

5.  **Ejecutar la aplicación:**
    Finalmente, ejecuta el script principal de la aplicación desde el directorio del proyecto:
    ```bash
    python main.py
    ```

# Desarrollado por: 
- Gabriel Gómez
- Armando Martinez
- María Malavé

# Metodologia de desarrollo:

1. **Requisitos del proyecto:**
    - El proyecto requiere la formulación de productos químicos utilizando IA.
    - Se utilizará Python como lenguaje de programación.
    - Se utilizará Ollama para ejecutar modelos de lenguaje localmente.
    - Se utilizará el modelo `llama3.2:3b` para procesar texto.
    - Se utilizará el modelo `llama3.2:3b` para procesar texto.

2. **Tecnica utilizada para el desarrollo del proyecto con IA (RAG):**
    - Se utilizará la tecnica de Retrieval Augmented Generation (RAG) para mejorar la calidad de la respuesta del modelo.

# Version: 1.0

# Fecha: 2025-12-07