from fastapi import APIRouter, HTTPException, Query, Path
from service.products import get_all_products
from schemas import Product

router = APIRouter()

@router.get("/")
def get_all_product():
    return get_all_products()

# /products?name="samsung"
@router.get("/by-name")
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
    
@router.get("/{product_id}")
def get_product_by_id(
    product_id: str = Path(..., 
        min_length=36, 
        max_length=36,
        description="UUID of the product", 
        example="8885a4ea-ce3f-7dd7-bee0-t4ccc70fea6a"
    ),
):
    products = get_all_products()
    
    # product = next((p for p in products if p["id"] == product_id), None)
    
    # for product in products:
    #     if product["id"] == product_id:
    #         return product
    # raise HTTPException(status_code=404, detail="Product not found")
    
    product = [p for p in products if p["id"] == product_id][0]
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.post("/")
def create_product(product: Product):
    # Now Product is the python dictionary object and we are converting it to the json(java script object notation)
    return product.model_dump(mode="json") 