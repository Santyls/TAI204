#importaciones
from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel,Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

#Instancia del servidor--------------------------------------------------------------------
app= FastAPI(
    title="Mi Primer API",
    description="Santiago L",
    version="1.0"
)

#TB Ficticia
usuarios=[
    {"id":1,"nombre":"Diego","edad":21},
    {"id":2,"nombre":"Coral","edad":21},
    {"id":3,"nombre":"Saul","edad":21}
]

#Gt, ge, lt, le: Restricciones numérica 
#(mayor que, mayor o igual, menor que, menor o igual) 
#Min_length, max_length: 
#Restricciones en la longitud de cadenas de texto. 
#Modelo Pydantic de validación---------------------------------------------------------

class crear_usuario(BaseModel):
    
    id: int = Field(...,gt=0, description= "identificador de usuario")
    nombre: str = Field(...,min_length=3, max_length= 50, example="Pepe Pecas")
    edad: int = Field(...,ge=1, le=125,description="Edad valida entre 1 y 125")

#Field(): Valores por defecto y restricciones. 
#Contint(): Rstricciones valores enteros en un rango. 
#Contstr(): Restricciones de cadenas con reglas específicas. 

#####################
#Seguridad
#####################

security= HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(security)):
    usuarioAut= secrets.compare_digest(credenciales.username, "Santy")
    contraAuth= secrets.compare_digest(credenciales.password, "123456")

    if not(usuarioAut and contraAuth):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail=" Credemciales no autorizadas"
        )
    return credenciales.username

#Endpoints
@app.get("/", tags=['Inicio'])
async def bienvenido():
    return{"menssaje":"Bienvenido a FastApi"}



@app.get("/holaMundo", tags=['Asincronia'])
async def Hola():
    await asyncio.sleep(5) #petición, condultaDB, Archivo
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
async def crear_usuario(usuario:crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code= 400,
                detail="El id ya existe"
            )
    usuarios.append(usuario)
    return{
        "Mensaje":"Usuario agregado",
        "Usuario":usuario,
        "status":200
    }


@app.put("/v1/usuarios/", tags=['CRUD HTTP'])
async def actualizar_usuario(usuario: dict):
    if "id" not in usuario:
        raise HTTPException(status_code=400, detail="El json debe incluir el campo 'id' para actualizar")
    for usr in usuarios:
        if usr.get("id") == usuario.get("id"):
            usr["nombre"] = usuario.get("nombre", usr["nombre"]) 
            usr["edad"] = usuario.get("edad", usr["edad"])
            
            return {
                "Mensaje": "Usuario actualizado",
                "Usuario": usr,
                "status": 200
            }
    
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede actualizar")


@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'])
async def eliminar_usuario(id: int, usuarioAuth:str=Depends(verificar_peticion)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            
            return {
                "Mensaje": f"Usuario eliminado por {usuarioAuth}",
                "status": 200   
            }
            
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede eliminar")


security = HTTPBasic()

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    usuarioAut = secrets.compare_digest(credenciales.username, "admin")
    contraAuth = secrets.compare_digest(credenciales.password, "123456")

    if not (usuarioAut and contraAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas"
        )
    return credenciales.username


class CategoriaEnum(str, Enum):
    opcion1 = "Activo"
    opcion2 = "Inactivo"

class MiModelo(BaseModel):
    # ID mayor a 0
    id: int = Field(..., gt=0, description="ID único")
    
    # Textos con longitud mínima y máxima
    nombre: str = Field(..., min_length=3, max_length=50, example="Juan")
    
    # Números enteros en un rango (ej. edades, años)
    edad: int = Field(..., ge=18, le=120, description="Debe ser mayor de edad")
    
    # Validar correos (Requiere EmailStr importado)
    correo: EmailStr = Field(..., example="usuario@correo.com")
    
    # Listas desplegables (Enum) con valor por defecto
    estado: CategoriaEnum = CategoriaEnum.opcion1

@app.delete("/recursos/{item_id}", tags=['Recursos Protegidos'])
async def eliminar_recurso(item_id: int, usuarioAuth: str = Depends(verificar_peticion)):
    # 1. Buscar el elemento por ID
    for db_item in elementos_db:
        if db_item["id"] == item_id:
            # 2. Eliminar de la lista
            elementos_db.remove(db_item)
            return {"mensaje": f"Recurso eliminado por {usuarioAuth}"}
            
    # 3. Si no lo encuentra
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")

@app.put("/recursos/{item_id}", tags=['Recursos Protegidos'])
async def actualizar_recurso(
    item_id: int, 
    nuevo_estado: CategoriaEnum, 
    usuarioAuth: str = Depends(verificar_peticion)
):
    # 1. Buscar el elemento por ID
    for db_item in elementos_db:
        if db_item["id"] == item_id:
            # 2. Actualizar el valor
            db_item["estado"] = nuevo_estado
            return {
                "mensaje": f"Actualizado por {usuarioAuth}", 
                "data": db_item
            }
            
    # 3. Si no lo encuentra, lanza error
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")

##@app.get("/recursos/", tags=['Recursos'])
##async def listar_recursos():
#    return {"total": len(elementos_db), "datos": elementos_db}

#@app.post("/recursos/", status_code=status.HTTP_201_CREATED, tags=['Recursos'])
#async def registrar_recurso(item: MiModelo):
    # 1. Validar si ya existe el ID
    #for db_item in elementos_db:
     #        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El ID ya existe")
   #         
  #  # 2. Guardar como diccionario
 #    
#    return {"mensaje": "Registro exitoso", "data": item}