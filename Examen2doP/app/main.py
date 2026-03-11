from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError



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

class Cliente(BaseModel):
    id_cliente: int = Field(...,gt=0, description= "identificador de usuario")
    nombre: str = Field(...,min_length=8, example="Pepe Pecas")
 #   edad: int = Field(...,ge=1, le=125,description="Edad valida entre 1 y 125")

class Turno(BaseModel):
    id_turno: int = Field(...,gt=0, description= "identificador de turno")
    id_cliente: int = Field(...,gt=0, description= "identificador de usuario")
    fecha: int = Field(..., gt=1450, le=datetime.now().year, description="")
    paginas: int = Field(..., gt=1, description="Debe tener más de 1 página")
    estado: TipoTramite = TipoTramite.consulta


#endpoints-----------------------------------------------------------------------------------
#Clientes -------------------------------------------
@app.post("/clientes", status_code=status.HTTP_201_CREATED, tags=['clientes'])#
async def registrar_libro(cliente: Cliente):
    # Verificamos si el cliente ya existe
    for c in clientes_db:
        if c["id_cliente"] == clientes_db.id_cliente:
            raise HTTPException(status_code=400, detail="El ID del cliente ya existe.")
    
    clientes_db.append(cliente.model_dump())
    
    return {"mensaje": "Cliente registrado exitosamente", "libro": cliente}

#turnos----------------------------------------------------------------------------

@app.post("/turnos", status_code=status.HTTP_201_CREATED, tags=['turnos'])
async def registrar_libro(turno: Turno):
    # Verificamos si el turno ya existe
    for t in turnos_db:
        if t["id_turno"] == turno.id_turno:
            raise HTTPException(status_code=400, detail="El ID del turno ya existe.")
            
    turnos_db.append(turnos_db.model_dump())
    
    return {"mensaje": "Turno registrado exitosamente", "turno": turno}