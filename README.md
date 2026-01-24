# QuimicAI 🧪

Asistente inteligente especializado en productos químicos domésticos, desarrollado con IA para proporcionar información segura y útil sobre ingredientes, recetas y seguridad química.

## 🎯 Características

- **Búsqueda Inteligente**: Consulta información sobre productos químicos usando lenguaje natural
- **Base de Conocimientos**: Amplia base de datos con ingredientes químicos, recetas y reglas de seguridad
- **Interfaz de Chat**: Interfaz web moderna con historial de conversaciones
- **IA Local**: Utiliza Ollama con LLaMA para respuestas precisas y privadas
- **Persistencia**: Las conversaciones se guardan automáticamente en el navegador

## 🚀 Instalación

### Requisitos Previos

1. **Python 3.8+**
2. **Ollama** instalado y corriendo ([instalar Ollama](https://ollama.ai))
3. **Modelo LLaMA**:
   ```bash
   ollama pull llama3.2:3b
   ```

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd Proyecto_inteligencia_artificial_productos_quimicos
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv env
   ```

3. **Activar entorno virtual**:
   - Windows:
     ```powershell
     .\env\Scripts\Activate.ps1
     ```
   - Linux/Mac:
     ```bash
     source env/bin/activate
     ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar variables de entorno** (opcional):
   ```bash
   cp .env.example .env
   # Editar .env según sea necesario
   ```

## ▶️ Uso

### Iniciar el Servidor

```bash
python backend/run.py
```

El servidor estará disponible en `http://localhost:5000`

### Usar la Aplicación

1. Abrir navegador en `http://localhost:5000`
2. Escribir consultas sobre productos químicos, por ejemplo:
   - "Vinagre Blanco"
   - "¿Cómo hago un limpiador casero?"
   - "¿Puedo mezclar cloro con vinagre?"
3. Las conversaciones se guardan automáticamente

## 🔧 Configuración

### Variables de Entorno

Crear un archivo `.env` basado en `.env.example`:

```env
# Modelo Ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# Servidor Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Timeouts
LLM_TIMEOUT=30
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Test específico
python tests/test_api.py
```

## 🏗️ Arquitectura

### Backend

- **Flask**: Servidor web y API REST
- **LangChain**: Framework para aplicaciones con LLM
- **Ollama**: Ejecución local de modelos de IA
- **FAISS**: Vector store para búsqueda semántica

### Frontend

- **HTML/CSS/JavaScript**: Interfaz web responsiva
- **localStorage**: Persistencia de conversaciones
- **Fetch API**: Comunicación con el backend

### Flujo de Datos

1. Usuario envía pregunta desde la interfaz web
2. Frontend envía request a `/api/ask`
3. Backend procesa la pregunta:
   - Busca documentos relevantes usando FAISS
   - Genera respuesta con LLaMA via Ollama
4. Respuesta se envía al frontend y se muestra al usuario

## 📝 API Endpoints

### `POST /api/ask`

Procesa una pregunta del usuario.

**Request:**
```json
{
  "question": "¿Qué es el vinagre blanco?"
}
```

**Response:**
```json
{
  "answer": "El vinagre blanco es...",
  "sources": [
    {"source": "inventario", "id": "ing_001"}
  ]
}
```

### `GET /api/health`

Health check del servicio.

**Response:**
```json
{
  "status": "ok",
  "assistant_ready": true
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## ⚠️ Advertencias

- Este asistente proporciona información general sobre productos químicos
- Siempre verificar información de seguridad con fuentes oficiales
- Usar equipo de protección apropiado al trabajar con químicos
- En caso de emergencia, contactar servicios médicos profesionales

## 👥 Autores

Proyecto Universitario - Inteligencia Artificial y Productos Químicos:

- Gabriel Gómez
- Armando Martinez
- María Malavé 
- Dariana Medina 
- Harlys Aguilar 
- Jhostin Vargas  
- Juan Yciarte 

## 🙏 Agradecimientos

- Ollama por proporcionar modelos de IA locales
- LangChain por el framework de desarrollo
- Comunidad open source