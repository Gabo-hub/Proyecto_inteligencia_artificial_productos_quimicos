
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.loader import KnowledgeLoader
from backend.core.config import AppConfig

def test_loader():
    config = AppConfig()
    print(f"Loading data from: {config.DATA_FILE}")
    
    docs = KnowledgeLoader.load_from_json(config.DATA_FILE)
    print(f"Total documents loaded: {len(docs)}")
    
    if len(docs) > 0:
        print("\n--- SAMPLE DOCUMENT (Chemical) ---")
        # Find a document with new fields (chem_XXX or one of the updated ones like ing_001)
        sample = next((d for d in docs if "Lejía" in d.page_content), docs[0])
        print(sample.page_content)
        
        print("\n--- SAMPLE DOCUMENT (Rule) ---")
        sample_rule = next((d for d in docs if "PELIGRO DE MEZCLA" in d.page_content), None)
        if sample_rule:
            print(sample_rule.page_content)
            
        print("\n--- SAMPLE DOCUMENT (Recipe) ---")
        sample_recipe = next((d for d in docs if "Receta:" in d.page_content and "bomba" in d.page_content.lower()), None)
        if sample_recipe:
            print(sample_recipe.page_content)
            
    else:
        print("No documents loaded.")

if __name__ == "__main__":
    test_loader()
