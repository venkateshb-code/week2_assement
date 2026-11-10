from pydantic import BaseModel, EmailStr, ConfigDict, Field

class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class CustomerUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)
