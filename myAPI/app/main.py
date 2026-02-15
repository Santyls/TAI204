#importaciones
from fastapi import FastAPI, status, HTTPException
import asyncio
from typing import Optional

#Instancia del servidor
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
async def agregar_usuario(usuario:dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
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
async def eliminar_usuario(id: int):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            
            return {
                "Mensaje": "Usuario eliminado",
                "status": 200
            }
            
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede eliminar")
