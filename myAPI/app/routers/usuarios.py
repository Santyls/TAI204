from fastapi import FastAPI, status, HTTPException, Depends, APIRouter 
#Importar la base de datos
from app.data.database import usuarios
#importar el modelo de datos
from app.models.usuarios import crear_usuario

#seguridad
from app.security.auth import verificar_peticion
from typing import Optional

from sqlalchemy.orm import Session
from app.data.db import SessionLocal

from app.data.db import get_db
from app.data.usuario import Usuario as usuarioDB

# Función para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/v1/usuarios",
    tags=["CRUD HTTP"]
)

@router.get("/")
async def leer_usuarios(db:Session= Depends(get_db)):
    queryUsuario= db.query(usuarioDB).all()
    return{
        "status":"200",
        "total":len(queryUsuario),
        "usuarios":queryUsuario
    }

@router.get("/")
async def consulta_todos(db: Session = Depends(get_db)):
    # Aquí ya puedes hacer consultas reales:
    # return db.query(Usuario).all()
    return {"status": "conectado a postgres"}


@router.post("/")
async def crear_usuario(usuarioP: crear_usuario, db: Session = Depends(get_db)):
    usuarioNuevo = usuarioDB(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(usuarioNuevo)
    db.commit()
    db.refresh(usuarioNuevo)
    return {"Mensaje": "Usuario agregado", "Usuario": usuarioNuevo, "status": 200}


@router.put("/")
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


@router.delete("/{id}")
async def eliminar_usuario(id: int, usuarioAuth:str=Depends(verificar_peticion)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            
            return {
                "Mensaje": f"Usuario eliminado por {usuarioAuth}",
                "status": 200   
            }
            
    raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede eliminar")
