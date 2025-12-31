from fastapi import FastAPI, HTTPException, Query
from service.products import get_all_products

app = FastAPI()

@app.get("/products")
def get_all_product():
    return get_all_products()

# /products?name="samsung"
@app.get("/products-by-name")
def get_product_by_name(
    name: str = Query(
        default=None, 
        min_length=1, 
        max_length=50, 
        description="Search product by name (case insensitive)"
    )
):
    products = get_all_products()
    filter_products = []
    
    if name:
        needle = name.strip().lower()
        filter_products = [p for p in products if needle in p.get("name", "").lower()]
        
        if not filter_products:
            raise HTTPException(status_code=404, detail=f"No product found matching name={name}")
        total = len(filter_products)
        
    else:
        filter_products = products
        total = len(filter_products)
        
    return {
        "total": total,
        "products": filter_products
    }
    