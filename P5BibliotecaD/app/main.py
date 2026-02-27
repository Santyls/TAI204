from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime
#Importaciones para el manejo de errores
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# Instancia del servidor
app = FastAPI(
    title="API de Biblioteca Digital",
    description="Control de libros y préstamos",
    version="1.0"
)

# Manejo de errores personalizados -----------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Faltan datos o los datos proporcionados no son válidos.",
            "errores_especificos": exc.errors()
        }
    )

#Listas de los datos
libros_db = []
prestamos_db = []

#Validaciones personalizadas mediante pydantic ------------------------------------------------------
#Para validar los estados de los libros, para que solo acepte disponible o prestado
class EstadoLibro(str, Enum):
    disponible = "disponible"
    prestado = "prestado"

#validaciones del libro
class Libro(BaseModel):
    id_libro: int
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del libro (2-100 caracteres)")
    year: int = Field(..., gt=1450, le=datetime.now().year, description="Año mayor a 1450 y no mayor al actual")
    paginas: int = Field(..., gt=1, description="Debe tener más de 1 página")
    estado: EstadoLibro = EstadoLibro.disponible


#validaciones para los prestamos
class Prestamo(BaseModel):
    id_prestamo: int
    id_libro: int
    nombre: str = Field(..., min_length=3)
    correo: EmailStr = Field(..., description="Correo electrónico válido")


#ENDPOINTS DE LIBROS ---------------------------------------------------------------------------------

#Registro de un libro PUT
@app.post("/libros/", status_code=status.HTTP_201_CREATED, tags=['Libros'])#se indica que regrese el estatus 201 cuando sea creado
async def registrar_libro(libro: Libro):
    # Verificamos si el libro ya existe
    for l in libros_db:
        if l["id_libro"] == libro.id_libro:
            raise HTTPException(status_code=400, detail="El ID del libro ya existe.")
    
    libros_db.append(libro.model_dump())
    
    return {"mensaje": "Libro registrado exitosamente", "libro": libro}

#Mostrar todos los libros registrados GET
@app.get("/libros/disponibles", tags=['Libros'])
async def listar_libros_disponibles():
    disponibles = [libro for libro in libros_db if libro["estado"] == "disponible"]
    return {"total": len(disponibles), "libros_disponibles": disponibles}

#Buscar un libro por su nombre
@app.get("/libros/buscar", tags=['Libros'])
async def buscar_libro(nombre: str):
    resultados = [libro for libro in libros_db if nombre.lower() in libro["nombre"].lower()]
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron libros con ese nombre")
    return {"resultados": resultados}


#ENDPOINTS DE PRÉSTAMOS ----------------------------------------------------------------------

#Registro de prestamos de libros
@app.post("/prestamos/", status_code=status.HTTP_201_CREATED, tags=['Préstamos'])
async def registrar_prestamo(prestamo: Prestamo):
    # se busca si el libro existe dentro de nuestra lista de libros, por id
    libro_encontrado = next((l for l in libros_db if l["id_libro"] == prestamo.id_libro), None)
    
    if not libro_encontrado:
        raise HTTPException(status_code=404, detail="El libro no existe.")
        
    #se verifica si ya esta prestado el libro
    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El libro ya se encuentra prestado")
    
    #se cambiar el estado a prestado
    libro_encontrado["estado"] = "prestado"
    
    #guarda o genera el prestamo con los datos puestos
    prestamos_db.append(prestamo.model_dump())
    
    return {"mensaje": "Préstamo registrado exitosamente", "prestamo": prestamo}

#Devolver libro, marca un 200 si esta todo bien, y 409 si no hay prestamo
@app.put("/prestamos/{id_libro}/devolver", status_code=status.HTTP_200_OK, tags=['Préstamos'])
async def devolver_libro(id_libro: int):
    #se busca el prestamo por id
    prestamo_activo = next((p for p in prestamos_db if p["id_libro"] == id_libro), None)
    
    if not prestamo_activo:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No existe un registro de préstamo para este libro.")
    
    #se actualiza el estado
    for l in libros_db:
        if l["id_libro"] == id_libro:
            l["estado"] = "disponible"
            break
            
    return {"mensaje": "Libro devuelto exitosamente"}

#Eliminar prestamo
@app.delete("/prestamos/{id_prestamo}", tags=['Préstamos'])
async def eliminar_registro_prestamo(id_prestamo: int):
    for p in prestamos_db:
        if p["id_prestamo"] == id_prestamo:
            prestamos_db.remove(p)
            return {"mensaje": "Registro de préstamo eliminado", "status": 200}
            
    raise HTTPException(status_code=404, detail="Registro de préstamo no encontrado")