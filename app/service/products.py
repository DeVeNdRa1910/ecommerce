import json
from typing import List, Dict
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent/"data"/"dummy.json"

def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, 'r', encoding="utf-8") as file:
        return json.load(file) 
    

def get_all_products() -> List[Dict]:
    return load_products()

def save_product(products: List[Dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=4, ensure_ascii=False)

def add_product(product: Dict) -> Dict:
    # first we need to checkt the comman sku, if we already have the product then why we need to create one more catagory
    products = get_all_products()
    
    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exist")
    
    products.append(product)
    save_product(products)
    
    return product

def remove_product(product_id:str) -> None:
    products = get_all_products()
    
    for idx, p in enumerate(products):
        if p["id"] == str(product_id):
            deleted = products.pop(idx)
            save_product(products)
            return {"message": "Product deleted successfully", "data": deleted}