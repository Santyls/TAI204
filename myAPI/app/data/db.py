from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
import os
#1definimos URL copnexion
DATABASE_URL= os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5432/db_miapi"
)

#2creamos ek motor en conexión
engine= create_engine(DATABASE_URL)

#Creamos gestion de sesiones
SessionLocal= sessionmaker(
    autocommit= False,
    autoflush= False,
    bind= engine
)

#4. Base declarativa para Modelo
Base= declarative_base()

#5. funcion que trabajara con peticiones 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()