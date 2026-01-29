#importaciones
from fastapi import FastAPI
import asyncio

#Instancia del servidor
app= FastAPI()


#Endpoints
@app.get("/")
async def bienvenido():
    return{"menssaje":"Bienvenido a FastApi"}



@app.get("/holaMundo")
async def Hola():
    await asyncio.sleep(5) #petición, condultaDB, Archivo
    return{
        "mensaje":"Hola Mundo FastAPI",
        "status":"200"
    }
    