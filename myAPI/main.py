#importaciones
from fastapi import FastAPI
import asyncio
from typing import Optional

#Instancia del servidor
app= FastAPI(
    title="Mi Primer API",
    descriptions="Santiago L",
    version="1.0"
)

#TB Ficticia
usuarios=[
    {"id":1,"nombre":"Diego","edad":21},
    {"id":1,"nombre":"Coral","edad":21},
    {"id":1,"nombre":"Saul","edad":21}
]

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
    
@app.get("/v1/usuario/{id}", tags=['Parametro Obligatorio'])
async def consultauno(id:int):

    return{"menssaje":"Usuario encontrado",
           "usuario":id,
           "status":"200"}

@app.get("/v1/usuarios/", tags=['Parametro Opcional'])
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuariosK in usuarios:
            if usuariosK["id"] == id:
                return{"mensaje":"Usuario encontrado","status":200}
        return{"mensaje":"usuario no encontrado", "status":"200"}
    else:
        return{"mnesaje":"No se proporciono id"}
