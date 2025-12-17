
from typing import Optional
from pydantic import BaseModel

# Entidad user
class User(BaseModel):
    id: Optional[str] = None
    name:str
    surname:str
    age: int


