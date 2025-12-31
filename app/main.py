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
    ),
    sort_by_price: bool = Query(
        default=False,
        description="Sort products by price",
    ),
    order: str = Query(
        default="asc",
        description="Sort order when sort_by_price=true (asc, desc)"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items"
    ), 
    offset: int = Query(
        default=0,
        ge=0, 
        description="Pagination offset"  
    )
):
    products = get_all_products()
    
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]
        
        if not products:
            raise HTTPException(status_code=404, detail=f"No product found matching name={name}")
        total = len(products)
        
    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", ""), reverse=reverse)
        
    products = products[offset: offset+limit]
    
    return {
        "total": total,
        "products": products
    }
    