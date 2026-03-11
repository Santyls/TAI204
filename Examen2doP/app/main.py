from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


#seguridad-----------------------------------------------------------
security= HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(security)):
    usuarioAut= secrets.compare_digest(credenciales.username, "banco")
    contraAuth= secrets.compare_digest(credenciales.password, "2468")

    if not(usuarioAut and contraAuth):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail=" Credemciales no autorizadas"
        )
    return credenciales.username
#---------------------------------------------------------------


app = FastAPI(
    title="API de Biblioteca Digital",
    description="Control de libros y préstamos",
    version="1.0"
)

#datos

tramites_db = []
turnos_db = []
clientes_db = []

#modelos

class TipoTramite(str, Enum):
    deposito = "déposito"
    retiro = "retiro"
    consulta = "consulta"

class EstadoTramite(str, Enum):
    atendido = "atendido"
    porAtender = "por atender"

class Cliente(BaseModel):
    id_cliente: int = Field(...,gt=0, description= "identificador de usuario")
    nombre: str = Field(...,min_length=8, example="Pepe Pecas")
    turnos: int

 #   edad: int = Field(...,ge=1, le=125,description="Edad valida entre 1 y 125")

class Turno(BaseModel):
    id_turno: int = Field(...,gt=0, description= "identificador de turno")
    id_cliente: int = Field(...,gt=0, description= "identificador de usuario")
    fecha: str = Field(..., description="")
    tipo: TipoTramite = TipoTramite.consulta
    estado: EstadoTramite = EstadoTramite.porAtender


#endpoints-----------------------------------------------------------------------------------
#Clientes ------------------------------------------- ya estÁ------------------------------------------------------
@app.post("/clientes/", status_code=status.HTTP_201_CREATED, tags=['clientes'])#
async def registrar_cliente(cliente: Cliente):
    # Verificamos si el cliente ya existe
    for c in clientes_db:
        if c["id_cliente"] == clientes_db.id_cliente:
            raise HTTPException(status_code=400, detail="El ID del cliente ya existe.")
    
    clientes_db.append(cliente.model_dump())
    
    return {"mensaje": "Cliente registrado exitosamente", "libro": cliente}

#turnos-----------------------------------------------------------------------------------------
#crear turno----------------------------------------------------------------------------------
@app.post("/turnos", status_code=status.HTTP_201_CREATED, tags=['turnos'])
async def registrar_turno(turno: Turno):
    # Verificamos si el turno ya existe
    for t in turnos_db:
        if t["id_turno"] == turno.id_turno:
            raise HTTPException(status_code=400, detail="El ID del turno ya existe.")
    
            
    turnos_db.append(turnos_db.model_dump())
    
    return {"mensaje": "Turno registrado exitosamente", "turno": turno}


#Listar turnos --------------------------------------------------------------------------------
@app.get("/turnos/", tags=['Turnos'])
async def listar_turnos():
    return {"total": len(turnos_db), "datos": turnos_db}

#consultar por id-----------------------------------------------------------------------------

@app.get("/turnos/{id}", tags=['Turnos'])
async def consultauno(id:int): 
        
    resultados = [id for id in turnos_db in id["id_turno"]]
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron turnos con ese id")

    return{"menssaje":"Turno encontrado",
           "usuario":id,
           "status":"200"}




#marcar como atendido------------------------------------------------------------------------------
@app.put("/turnos/{item_id}", tags=['Turnos'])
async def actualizar_turno(
    turno_id: int, 
    nuevo_estado: EstadoTramite.atendido, 
    usuarioAuth: str = Depends(verificar_peticion)
):
    # 1. Buscar el elemento por ID
    for db_item in turnos_db:
        if db_item["id_turno"] == turno_id:
            # 2. Actualizar el valor
            db_item["estado"] = nuevo_estado
            return {
                "mensaje": f"Actualizado por {usuarioAuth}", 
                "data": db_item
            }
            
    # 3. Si no lo encuentra, lanza error
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")

#eliminar -----------------------------------------------------------------------------

@app.delete("/turno/{item_id}", tags=['Turnos'])
async def eliminar_recurso(item_id: int, usuarioAuth: str = Depends(verificar_peticion)):
    # 1. Buscar el elemento por ID
    for db_item in turnos_db:
        if db_item["id_turno"] == item_id:
            # 2. Eliminar de la lista
            turnos_db.remove(db_item)
            return {"mensaje": f"Turno eliminado por {usuarioAuth}"}
            
    # 3. Si no lo encuentra
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso no encontrado")


#no permitir mas de 5 turnos por dia a un cliente, 
#fecha turno futura entre 9:00am y 3:00pm 