# importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
import jwt 

########## Configuraciones de Seguridad para JWT
SECRET_KEY = "mi_clave_secreta_super_segura" # ya en un ambiente real esto tendria que ir en un archivo .env
ALGORITHM = "HS256" # es el algoritmo que generalmente se usa en JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 1 # establecemos el tiempo de 30 minutos, puede ser más, poquito menos

# Instancia del servidor -------------------------------------------------------------------------------------------------------
app= FastAPI(
    title="Mi API JWT",
    description="API protegida con OAuth2, JWT y contraseñas reales",
    version="1.0"
)

# TB Ficticia (AHORA CON CONTRASEÑAS)
usuarios=[
    {"id":1,"nombre":"Diego","edad":21, "password": "mipassword1"},
    {"id":2,"nombre":"Coral","edad":21, "password": "mipassword2"},
    {"id":3,"nombre":"Saul","edad":21, "password": "mipassword3"}
]

# Modelo de validaciones de usuario --------------------------
class crear_usuario(BaseModel):
    id: int = Field(...,gt=0, description= "identificador de usuario")
    nombre: str = Field(...,min_length=3, max_length= 50, example="Pepe Pecas")
    edad: int = Field(...,ge=1, le=125,description="Edad valida entre 1 y 125")
    password: str = Field(...,min_length=4, description="Contraseña segura del usuario")


#####################
# Seguridad OAuth2 + JWT
#####################

#Configurar OAuth2 ----------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Generar Tokens -------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#Implementar validación de tokens ---------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


#####################
# Endpoints
#####################

# Autenticación y obtención del tokens --------------------------------------------------------------------------------
@app.post("/login", tags=['Autenticación'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario_encontrado = None
    for usr in usuarios:
        if usr["nombre"] == form_data.username:
            usuario_encontrado = usr
            break
            
    # Validamos que el usuario exista y que la contraseña coincida con la de nuestros datos ficticios
    if not usuario_encontrado or usuario_encontrado.get("password") != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario_encontrado["nombre"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/", tags=['Inicio'])
async def bienvenido():
    return{"menssaje":"Bienvenido a FastApi con JWT"}

@app.get("/holaMundo", tags=['Asincronia'])
async def Hola():
    await asyncio.sleep(5)
    return{
        "mensaje":"Hola Mundo FastAPI",
        "status":"200"
    }
    
@app.get("/v1/ParametroOb/{id}", tags=['Parametro Obligatorio'])
async def consultauno(id:int):
    return{"menssaje":"Usuario encontrado",
           "usuario":id,
           "status":"200"}

@app.get("/v1/ParemtroOp/", tags=['Parametro Opcional'])
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuariosK in usuarios:
            if usuariosK["id"] == id:
                return{"mensaje":"Usuario encontrado","status":200}
        return{"mensaje":"usuario no encontrado", "status":200}
    else:
        return{"mnesaje":"No se proporciono id"}

@app.get("/v1/usuarios/", tags=['CRUD HTTP'])
async def consultaT():
    return {
        "status":"200",
        "total": len(usuarios),
        "Usuarios": usuarios
    } 

@app.post("/v1/usuarios/", tags=['CRUD HTTP'])
async def crear_usuario_endpoint(usuario:crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code= 400,
                detail="El id ya existe"
            )
    # Guarda al usuario con todo y su contraseña
    usuarios.append(usuario.model_dump())
    return{
        "Mensaje":"Usuario agregado",
        "Usuario":usuario,
        "status":200
    }

# PUT Usuarios protegidos--------------------------------------------------------------------------------------------
@app.put("/v1/usuarios/", tags=['CRUD HTTP'])
async def actualizar_usuario(usuario: dict, usuarioAuth: str = Depends(get_current_user)):
    if "id" not in usuario:
        raise HTTPException(status_code=400, detail="El json debe incluir el campo 'id' para actualizar")
    for usr in usuarios:
        if usr.get("id") == usuario.get("id"):
            usr["nombre"] = usuario.get("nombre", usr["nombre"]) 
            usr["edad"] = usuario.get("edad", usr["edad"])
            if "password" in usuario:
                usr["password"] = usuario.get("password")
            
            return {
                "Mensaje": f"Usuario actualizado exitosamente por {usuarioAuth}",
                "Usuario": usr,
                "status": 200
            }
    
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede actualizar")

@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'])
async def eliminar_usuario(id: int, usuarioAuth: str = Depends(get_current_user)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            
            return {
                "Mensaje": f"Usuario eliminado por {usuarioAuth}",
                "status": 200   
            }
            
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede eliminar")