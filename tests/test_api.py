"""
Script de prueba para verificar la conexión del frontend con el backend
"""
import requests
import json

# URL del servidor Flask
API_URL = "http://127.0.0.1:5000/ask"

def test_connection():
    """Prueba la conexión con el servidor"""
    try:
        print("🔍 Probando conexión con el servidor...")
        response = requests.post(
            API_URL,
            json={"question": "Hola, ¿estás funcionando?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor respondió correctamente!")
            print(f"\n📝 Respuesta: {data.get('answer', 'Sin respuesta')}")
            print(f"\n📚 Fuentes: {data.get('sources', [])}")
        else:
            print(f"❌ Error: Código de estado {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor.")
        print("Verifica que el servidor Flask esté corriendo en http://127.0.0.1:5000")
    except requests.exceptions.Timeout:
        print("⏱️ El servidor tardó demasiado en responder (timeout)")
        print("Esto puede ser normal si Ollama está cargando el modelo por primera vez")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_connection()
