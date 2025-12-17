from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth_users import auth_user

router = APIRouter(prefix="/products",
                   tags=["products"])

# Entidad user
class Product(BaseModel):
    id: int
    name:str
    price:float
    id_user: int
    
# la siguiente lista pretende simular una base de datos para probar nuestra API
products_list = [Product(id=1, name = "Ratón", price = 9.99, id_user=1),
              Product(id=2, name = "Teclado", price = 19.99, id_user=1),
              Product(id=3, name = "Monitor", price = 129.99, id_user=2)]

@router.get("/")
def products():
    return products_list


@router.get("/{id}", response_model=Product)
def product(id: int):
    products = search_product(id)
    if len(products) != 0:
        return products[0]
    raise HTTPException(status_code=404, detail="User not found")

# Petición anidada
@router.get("/{id}", response_model=Product)
def product(id: int):
    pass

@router.post("/", status_code=201, response_model=Product)
def add_product(product: Product, user = Depends(auth_user)):
       
    # Calculamos nuevo id y lo modificamos al usuario a añadir
    product.id = next_id()
    # Añadimos el usuario a nuestra lista
    products_list.append(product)
    # La respuesta de nuestro método es el propio usuario añadido
    return product
    
@router.put("/{id}", response_model=Product)
def modify_product(id: int, product: Product):
    # El método enumerate devuelve el índice de la lista 
    # y el usuario almacenado en dicho índice
    for index, saved_product in enumerate(products_list):
        if saved_product.id == id:
            product.id = id
            products_list[index] = product
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{id}", response_model=Product)
def delete_product(id:int):
    for saved_product in products_list:
        if saved_product.id == id:
            products_list.remove(saved_product)
            return {}
    raise HTTPException(status_code=404, detail="Product not found")
   
def search_product(id: int):
    #users = filter(lambda user: user.id==id, users_list)
    return [product for product in products_list if product.id == id]

def next_id():
    # Calculamos el usuario con el id más alto 
    # y le sumamos 1 a su id   
    return max([product.id for product in products_list]) + 1