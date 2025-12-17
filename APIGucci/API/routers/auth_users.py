from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Librería JWT
import jwt

# Para trabajar las excepciones de los tokens
from jwt.exceptions import InvalidTokenError, PyJWTError

# Librería para aplicar un hash a la contraseña
from pwdlib import PasswordHash

# Definimos el algoritmo de encriptación
ALGORITHM = "HS256"

# Duración del token
ACCESS_TOKEN_EXPIRE_MINUTES = 1

# Clave que se utilizará como semilla para generar el token
# openssl rand -hex 32
SECRET_KEY = "87ab51098990feb4a2f78da9c911187a71290ebd9e98e56d8b24090815f2ce6f"

# Objeto que se utilizará para el cálculo del hash y 
# la verificación de las contraseñas
password_hash = PasswordHash.recommended()

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    username: str
    fullname:str
    email:str
    disabled: bool | None = False

class UserDB(User):
    hashed_password: str


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "fullname": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False
    }
}

 

def search_user_db(username: str):
    if username in fake_users_db:
        return UserDB(fake_users_db[username])
    

# Esta función será nuestra dependencia
# Lo que pretendemos con esta función es que 
# nos devuelva el usuario a partir del token
# En esta función, nuestra relación de dependencia es el objeto oauth2
async def auth_user(token:str = Depends(oauth2)):    
    # Nos creamos un objeto para almacenar la excepción que vamos a lanzar en varias ocasiones
    exception = HTTPException(status_code=401, 
                            detail="Credenciales de autenticación inválidas", 
                            headers={"WWW-Authenticate" : "Bearer"})
     
    # Como la llamada a get puede lanzar una excepción, la capturamos por si acaso
    try:        
        # Para poder obtener el usuario a partir del token tenemos que desencriptarlo
        # con exactamente las mismas características que para encriptarlo
        username = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("sub")
        # Nos aseguramos de que el usuario no es None
        if username is None:
            # Si es None lanzamos la excepción
            raise HTTPException(status_code=401, 
                            detail="Credenciales de autenticación inválidas", 
                            headers={"WWW-Authenticate" : "Bearer"})       
    except PyJWTError:
        # Si ha fallado algo del proceso de la decodificación o si no ha encontrado la clave "sub"
        # lanzamos una excepción HTTP
        raise HTTPException(status_code=401, 
                            detail="Credenciales de autenticación inválidas", 
                            headers={"WWW-Authenticate" : "Bearer"})
        
    # Si hemos llegado a este punto es que no se ha producido ninguna excepción
    # y tenemos un usuario válido
    user = User(**fake_users_db[username])

    if user.disabled:
        # Si el usuario está deshabilitado lanzamos excepción
        raise HTTPException(status_code=400, 
                            detail="Usuario inactivo")   

    # Retornamos un usuario correcto y habilitado
    return user


@router.post("/register", status_code=201)
async def register_user(user: UserDB):
    print("entro en el registro")
    # Hay que hashear la contraseña
    new_password = password_hash.hash(user.hashed_password)
    user.hashed_password = new_password
    fake_users_db[user.username] = user.model_dump()
    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):    

    # Miramos si el usuario existe en la Base de Datos
    user_db = fake_users_db.get(form.username)   
    # Si no está en la base de datos se lanza una excepción
    if not user_db:
        raise HTTPException(status_code = 400, detail="Usuario no encontrado")
    # Si está, creamos un objeto de tipo UserDB a partir de su información
    user = UserDB(**fake_users_db[form.username])

    # Comprobamos que las contraseñas coinciden con verify
    if not password_hash.verify(form.password, user.hashed_password):
        # Si no coinciden lanzamos excepción
        raise HTTPException(status_code=400, detail="La contraseña no es correcta")  

    # Tomamos la hora actual + el tiempo de expiración del token que es un min
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Parámetros de nuestro token: el ufake_users_dbsuario, fecha de expiración
    access_token = {"sub" : user.username, "exp":expire}
    # Para generar el token le pasamos la información a cifrar que es el usuario en sí y la fecha de expiración
    # También le pasamos la semilla y el algoritmo utilizado para generar el token
    token = jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM)
    # Si todo va bien, devolvemos el token generado
    return {"access_token" : token, "token_type": "bearer"}

@router.get("/auth/me")
async def me(user: User = Depends(auth_user)):
    return user