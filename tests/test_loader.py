from verify_logic import cargar_base_conocimiento

docs = cargar_base_conocimiento()
print(f"Total documents loaded: {len(docs)}")
if len(docs) > 0:
    print("First document sample:")
    print(docs[0].page_content)
else:
    print("No documents loaded.")
