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

# GET (ID)
@router.get("/{id}")
async def consulta_uno(id: int, db: Session = Depends(get_db)):
    # Buscamos en la BD el primer registro que coincida con el ID
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "mensaje": "Usuario encontrado",
        "usuario": usuario,
        "status": 200
    }


@router.post("/")
async def crear_n_usuario(usuarioP: crear_usuario, db: Session = Depends(get_db)):
    usuarioNuevo = usuarioDB(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(usuarioNuevo)
    db.commit()
    db.refresh(usuarioNuevo)
    return {"Mensaje": "Usuario agregado", "Usuario": usuarioNuevo, "status": 200}


# PUT - Actualización completa
@router.put("/{id}")
async def actualizar_usuario(id: int, usuarioP: crear_usuario, db: Session = Depends(get_db)):
    # Buscamos si existe el id ingresado
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede actualizar")
    
    # Reemplazamos todos sus campos, en este caso nombre y edad
    usuario.nombre = usuarioP.nombre
    usuario.edad = usuarioP.edad
    
    db.commit() # Guardamos cambios en la db
    db.refresh(usuario)
    
    return {
        "Mensaje": "Usuario actualizado correctamente",
        "Usuario": usuario,
        "status": 200
    }


# PATCH
@router.patch("/{id}")
async def modificar_usuario(id: int, campos: dict, db: Session = Depends(get_db)):
    # Buscamos si existe un usuario con ese ID
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Solo actualizamos lo que el usuario haya mandado en el JSON, si es nombre, nombre , y edad, pues edad.
    if "nombre" in campos:
        usuario.nombre = campos["nombre"]
    if "edad" in campos:
        usuario.edad = campos["edad"]
    # Se actualiza el registro
    db.commit()
    db.refresh(usuario)
    
    return {
        "Mensaje": "Usuario modificado parcialmente",
        "Usuario": usuario,
        "status": 200
    }


# DELETE
@router.delete("/{id}")
async def eliminar_usuario(id: int, usuarioAuth: str = Depends(verificar_peticion), db: Session = Depends(get_db)):
    # Buscamos si existe el usuario del ID
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado, no se puede eliminar")
    
    # Lo eliminamos usando el método delete de SQLAlchemy
    db.delete(usuario)
    db.commit() # Actualizamos el registro
    
    return {
        "Mensaje": f"Usuario eliminado por {usuarioAuth}",
        "status": 200   
    }
