
from fastapi import APIRouter
import asyncio
from typing import Optional
from app.data.database import usuarios
from app.models.usuarios import crear_usuario
import asyncio

routerV =APIRouter(
    prefix="/varios",
    tags=["varios"]
)
#Endpoints
@routerV.get("/")
async def bienvenido():
    return{"menssaje":"Bienvenido a FastApi"}



@routerV.get("/")
async def Hola():
    await asyncio.sleep(5) #petición, condultaDB, Archivo
    return{
        "mensaje":"Hola Mundo FastAPI",
        "status":"200"
    }
    
@routerV.get("/{id}")
async def consultauno(id:int):

    return{"menssaje":"Usuario encontrado",
           "usuario":id,
           "status":"200"}

@routerV.get("/")
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuariosK in usuarios:
            if usuariosK["id"] == id:
                return{"mensaje":"Usuario encontrado","status":200}
        return{"mensaje":"usuario no encontrado", "status":200}
    else:
        return{"mnesaje":"No se proporciono id"}

