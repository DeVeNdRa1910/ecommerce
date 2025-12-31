from fastapi import FastAPI
from api.v1 import products

app = FastAPI()
app.include_router(products.router, prefix="/products", tags=["product"])