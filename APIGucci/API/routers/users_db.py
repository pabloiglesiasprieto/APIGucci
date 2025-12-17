from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth_users import auth_user
from db.models.user import User
from db.client import db_client
from db.schemas.user import user_schema, users_schema

from bson import ObjectId

router = APIRouter(prefix="/usersdb", tags=["usersdb"])


# la siguiente lista pretende simular una base de datos para probar nuestra API
users_list = []


@router.get("/", response_model=list[User])
async def users():
    # El método find() sin parámetros devuelve todos los registros
    # de la base de datos
    return users_schema(db_client.APIDB.users.find())


# Método get tipo query. Sólo busca por id
@router.get("", response_model=User)
async def user(id: str):
    return search_user_id(id)


# Método get por id
@router.get("/{id}", response_model=User)
async def user(id: str):
    return search_user_id(id)


@router.post("/", response_model=User, status_code=201)
async def add_user(user: User):
    # print("dentro de post")
    if type(search_user(user.name, user.surname)) == User:
        raise HTTPException(status_code=409, detail="User already exists")

    user_dict = user.model_dump()
    del user_dict["id"]
    # Añadimos el usuario a nuestra base de datos
    # También podemos obtner con inserted_id el id que la base de datos
    # ha generado para nuestro usuario
    id = db_client.APIDB.users.insert_one(user_dict).inserted_id

    # Añadimos el campo id a nuestro diccionario. Hay que hacerle un cast
    # a string puesto que el id en base de datos se almacena como un objeto,
    # no como un string
    user_dict["id"] = str(id)

    # La respuesta de nuestro método es el propio usuario añadido
    # Creamos un objeto de tipo User a partir del diccionario user_dict
    return User(**user_dict)


@router.put("/{id}", response_model=User)
async def modify_user(id: str, new_user: User):
    # Convertimos el usuario a un diccionario
    user_dict = new_user.model_dump()
    # Eliminamos el id en caso de que venga porque no puede cambiar
    del user_dict["id"]
    try:
        # Buscamos el id en la base de datos y le pasamos el diccionario con los datos
        # a modificar del usuario
        db_client.APIDB.users.find_one_and_replace({"_id": ObjectId(id)}, user_dict)
        # Buscamos el objeto en base de datos y lo retornamos, así comprobamos que efectivamente
        # se ha modificado
        return search_user_id(id)
    except:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}", response_model=User)
async def delete_user(id: str):
    found = db_client.APIDB.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_schema(found))


# El id de la base de datos es un string, ya no es un entero
def search_user_id(id: str):
    # Si algo va mal en la búsqueda dentro de la base de datos se lanzará una excepción,
    # así que la controlamos
    try:
        # El id en base de datos no se guarda como un string, sino que es un objeto
        # Realizamos la conversión
        user = user_schema(db_client.APIDB.users.find_one({"_id": ObjectId(id)}))
        # Necesitamos convertirlo a un objeto User.
        return User(**user)
    except:
        return {"error": "User not found"}


def search_user(name: str, surname: str):
    # La búsqueda me devuelve un objeto del tipo de la base de datos.
    # Necesitamos convertirlo a un objeto User.
    try:
        # Si algo va mal en la búsqueda dentro de la base de datos se lanzará una excepción,
        # así que la controlamos
        user = user_schema(
            db_client.APIDB.users.find_one({"name": name, "surname": surname})
        )
        return User(**user)
    except:
        return {"error": "User not found"}


def next_id():
    # Calculamos el usuario con el id más alto
    # y le sumamos 1 a su id
    return (max(user.id for user in users_list)) + 1
