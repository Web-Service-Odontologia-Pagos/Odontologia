# app/database.py

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import Generator

# La ruta donde se guardará el archivo de base de datos SQLite (usando tu formato)
DATABASE_URL = "sqlite:///./users.db" 

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# === MODELOS DE BASE DE DATOS PARA HU-1, HU-2, HU-5 y HU-6 ===

class PacienteDB(Base):
    """Modelo de la tabla Pacientes (Usado en HU-1 y HU-6)."""
    __tablename__ = "pacientes"
    id_paciente = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    email = Column(String) 
    telefono = Column(String)
    
    facturas = relationship("FacturaDB", back_populates="paciente")

class FacturaDB(Base):
    """Modelo de la tabla Facturas (Central para HU-1, HU-2, HU-5)."""
    __tablename__ = "facturas"
    id_factura = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"))
    monto_total = Column(Float, nullable=False)
    estado_factura = Column(String, nullable=False) # 'Pendiente', 'Pagada'
    
    paciente = relationship("PacienteDB", back_populates="facturas")

class PagoDB(Base):
    """Modelo de la tabla Pagos (Central para HU-2, HU-5 y HU-6)."""
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True)
    id_factura = Column(Integer, ForeignKey("facturas.id_factura"))
    monto_pagado = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    estado_pago = Column(String, nullable=False) # 'En Proceso', 'Pagado', 'Rechazado'
    transaccion_bancaria_id = Column(String, unique=True, index=True)


Base.metadata.create_all(bind=engine)

# Función de inyección de dependencia
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()