from pydantic import (
    BaseModel, 
    Field, 
    AnyUrl, 
    field_validator, 
    model_validator, 
    computed_field, 
    EmailStr
)
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime

# We have three type of validators in pydantic -> field-validator, model_validator and compute_field
# XIAO-359GB-001 is the formate of the sku, to validate it we have validator's

# Create pydantic
class Seller(BaseModel):
    id: UUID = Field(alias="seller_id")
    name: str = Field(..., min_length=4)
    website: AnyUrl
    email: EmailStr  # Here we want to validate the email field only for that we can use field validator
    
    
    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        allwed_domain = ["mistore.in", "realmeofficial.in", "samsungindia.in", "lenovostore.in", "hpworld.in", "applestoreindia.in", "dellexclusive.in", "sonycenter.in", "oneplusstore.in", "asusexclusive.in", "gmail.com"]
        domain = str(value).split("@")[-1].lower()
        if domain not in allwed_domain:
            raise ValueError(f"Seller email domain not allowed: {domain}") 
        return value
    
class Dimension(BaseModel):
    length: Annotated[float, Field(gt=0, strict=True, description="Length in cm")]
    width: Annotated[float, Field(gt=0, strict=True, description="Width in cm")]
    height: Annotated[float, Field(gt=0, strict=True, description="Height in cm")]

class Product(BaseModel):
    id: UUID
    name: str = Field(..., min_length=4)
    sku: Annotated[str, Field(
        min_length=6,
        max_length=30,
        title="SKU",
        description="Stock Keeping Unit",
        example=["734-hjd-378-3d", "asdasd-asd-sad"]
    )]
    description: str
    category: str
    brand: str
    price: int 
    currency: Literal["INR"]="INR"
    discount_percent: int
    stock: int
    is_active: bool
    rating: float
    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Up to 10 tags ")
    ]
    image_urls: Annotated[
        Optional[List[AnyUrl]],
        Field(min_length=1, description="Atleas 1 image url")
    ]
    dimensions_cm: Dimension
    seller: Seller 
    created_at: datetime
    
    # In python input is taking in the string bydefault, if we want to perform any operation then we have to convert them, before converting mode will be "before" and after converting mode will be "after" 
    # Here we are converting(in suitable for perticular operation) the data with the help of pydantic
    # filed_validator is working on single field only 
    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_formate(cls, value: str):
        if "-" not in value:
            raise ValueError("SKU must have '-' ")
        
        last_three_digit = value.split("-")[-1]
        
        if not (len(last_three_digit)==3 and last_three_digit.isdigit()):
            raise ValueError("SKU must end with 3-digit sequance like -234 ")
        
        return value 
    
    # model validator is working on the complete model
    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "Product"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is zero then is_active must be false")
         
        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("Discounted product must have rating")
        
        return model
    
    # For final price we have to substract the discount from the price. For that kind of work we have compute_field
    @computed_field
    @property
    def calculate_price_after_discount(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)
    
    @computed_field
    @property
    def calculate_volume(self) -> float:
        d = self.dimensions_cm
        return round(d.height * d.length * d.width, 2)
    
    
# Update pydantic
class SellerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=4)
    website: Optional[AnyUrl] = None
    email: Optional[EmailStr] = None  # Here we want to validate the email field only for that we can use field validator
    
    
    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: Optional[EmailStr]):
        if value is None:
            return value
        allwed_domain = [
            "mistore.in", "realmeofficial.in", "samsungindia.in",
            "lenovostore.in", "hpworld.in", "applestoreindia.in",
            "dellexclusive.in", "sonycenter.in", "oneplusstore.in",
            "asusexclusive.in", "gmail.com"
        ]
        domain = str(value).split("@")[-1].lower()
        if domain not in allwed_domain:
            raise ValueError(f"Seller email domain not allowed: {domain}") 
        return value
    
class DimensionUpdate(BaseModel):
    length: Annotated[Optional[float], Field(gt=0, strict=True, description="Length in cm")] = None
    width: Annotated[Optional[float], Field(gt=0, strict=True, description="Width in cm")] = None
    height: Annotated[Optional[float], Field(gt=0, strict=True, description="Height in cm")] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=4)
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[Literal["INR"]] = None
    discount_percent: Optional[int] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    rating: Optional[float] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[AnyUrl]] = None
    dimensions_cm: Optional[DimensionUpdate] = None
    seller: Optional[SellerUpdate] = None

    # model validator is working on the complete model
    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "ProductUpdate"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is zero then is_active must be false")
        if model.discount_percent and model.discount_percent > 0:
            if model.rating is not None and model.rating == 0:
                raise ValueError("Discounted product must have rating")
        return model
