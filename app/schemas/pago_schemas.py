# app/schemas/pago_schemas.py

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Modelo anidado para cada línea de factura
class FacturaDetalle(BaseModel):
    id_factura: int
    monto_total: float = Field(..., alias="monto")
    estado_factura: str = Field(..., alias="estado")

    # Configuración de Pydantic para mapear de SQLAlchemy (ORM)
    class Config:
        from_attributes = True
        populate_by_name = True 

# Modelo principal de Respuesta para HU-1 (ConsultaF)
class ConsultaFResponse(BaseModel):
    mensaje: str
    fecha_proceso: datetime
    capital_total: float
    intereses_causados: float
    intereses_contingentes: float
    detalle_facturas: List[FacturaDetalle] 
    success: bool
    
    class Config:
        from_attributes = True