# Define the shape and validation rules of data entering and leaving your API.
from pydantic import BaseModel, EmailStr, Field

# # Defines and validates the data required when registering a new user.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$', description="Username must be alphanumeric and can include underscores.")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Password must be between 8 and 128 characters.")

# Defines the safe user information that can be returned by the API.
class UserPublic(BaseModel):
    username: str
    email: EmailStr
    
# Defines the safe user information that can be returned by the API.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    