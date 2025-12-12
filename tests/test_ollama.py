"""
Script de diagnóstico para probar la conexión con Ollama
"""
import sys
import time

print("🔍 Probando conexión con Ollama...")
print("-" * 50)

# Test 1: Importar librerías
print("\n1️⃣ Importando librerías...")
try:
    from langchain_ollama import OllamaLLM, OllamaEmbeddings
    print("   ✅ Librerías importadas correctamente")
except ImportError as e:
    print(f"   ❌ Error al importar: {e}")
    sys.exit(1)

# Test 2: Crear instancia de LLM
print("\n2️⃣ Creando instancia de LLM...")
try:
    llm = OllamaLLM(model="llama3.2:3b")
    print("   ✅ LLM creado correctamente")
except Exception as e:
    print(f"   ❌ Error al crear LLM: {e}")
    sys.exit(1)

# Test 3: Probar generación simple
print("\n3️⃣ Probando generación de texto...")
try:
    start = time.time()
    response = llm.invoke("Di solo 'Hola'")
    elapsed = time.time() - start
    print(f"   ✅ Respuesta recibida en {elapsed:.2f}s")
    print(f"   📝 Respuesta: {response}")
except Exception as e:
    print(f"   ❌ Error al generar texto: {e}")
    sys.exit(1)

# Test 4: Crear embeddings
print("\n4️⃣ Creando embeddings...")
try:
    start = time.time()
    embeddings = OllamaEmbeddings(model="llama3.2:3b")
    print("   ⏳ Embeddings creados, probando generación...")
    
    # Probar con un texto simple
    test_embedding = embeddings.embed_query("test")
    elapsed = time.time() - start
    print(f"   ✅ Embedding generado en {elapsed:.2f}s")
    print(f"   📊 Dimensión del vector: {len(test_embedding)}")
except Exception as e:
    print(f"   ❌ Error al crear embeddings: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ Todas las pruebas pasaron correctamente!")
print("=" * 50)
