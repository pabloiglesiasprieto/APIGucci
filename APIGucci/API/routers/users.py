from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth_users import auth_user

router = APIRouter(prefix="/users",
                   tags=["users"])

# Entidad user
class User(BaseModel):    
    name:str
    surname:str
    age: int

class UserID(User):
    id: int

# la siguiente lista pretende simular una base de datos para probar nuestra API
users_list = [UserID(id=1, name = "Paco", surname="Pérez", age=30),
              UserID(id=2, name = "María", surname="Martínez", age=20),
              UserID(id=3, name = "Lucía", surname="Rodríquez", age=40)]

@router.get("/")
def users():
    return users_list

@router.get("/", response_model=UserID)
def user(id: int):
    users = search_user(id)
    if len(users) != 0:
        return users[0]
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/{id}", response_model=UserID)
def user(id: int):
    users = search_user(id)
    if len(users) != 0:
        return users[0]
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/", status_code=201, response_model=UserID)
def add_user(user: User):
    # Calculamos nuevo id y lo modificamos al usuario a añadir
    new_id = next_id()
    new_user = UserID(id=new_id, **user.model_dump())
    # Añadimos el usuario a nuestra lista
    users_list.append(new_user)
    # La respuesta de nuestro método es el propio usuario añadido
    return new_user
    
@router.put("/{id}", response_model=User)
def modify_user(id: int, user: User):
    # El método enumerate devuelve el índice de la lista 
    # y el usuario almacenado en dicho índice
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            user.id = id
            users_list[index] = user
            return user
    
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{id}", response_model=User)
def delete_user(id:int):
    for saved_user in users_list:
        if saved_user.id == id:
            users_list.remove(saved_user)
            return {}
    raise HTTPException(status_code=404, detail="User not found")
   
def search_user(id: int):
    #users = filter(lambda user: user.id==id, users_list)
    return [user for user in users_list if user.id == id]

def next_id():
    # Calculamos el usuario con el id más alto 
    # y le sumamos 1 a su id
    return (max(user.id for user in users_list))+1