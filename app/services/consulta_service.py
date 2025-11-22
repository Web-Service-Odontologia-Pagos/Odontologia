# app/services/consulta_service.py

from app.schemas.pago_schemas import FacturaDetalle
from app.repository.pagos_repository import PagosRepository
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

class ConsultaService:
    def __init__(self, db: Session):
        # El servicio recibe la sesión de BD y la pasa al repositorio
        self.repo = PagosRepository(db) 

    def consultar_facturas_pendientes(self, id_paciente: int) -> Dict[str, Any]:
        
        facturas_db_data = self.repo.obtener_facturas_pendientes_por_paciente(id_paciente)

        # 1. Manejo de error: Paciente no encontrado (Código HTTP 404)
        if facturas_db_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"mensaje": "ID de paciente inválido o no encontrado.", "success": False}
            )
        
        # 2. Manejo de caso límite: Sin facturas pendientes (Código HTTP 200, success: false)
        if not facturas_db_data:
            return {
                "mensaje": "No existen saldos consolidados para el paciente.",
                "fecha_proceso": datetime.now(),
                "capital_total": 0.0,
                "intereses_causados": 0.0,
                "intereses_contingentes": 0.0,
                "detalle_facturas": [],
                "success": False
            }

        # 3. Consolidación y Mapeo
        capital_total = sum(factura.monto_total for factura in facturas_db_data)
        
        # Mapea los objetos ORM (FacturaDB) al modelo Pydantic (FacturaDetalle)
        detalle_facturas_pydantic = [
            FacturaDetalle.model_validate(item) 
            for item in facturas_db_data
        ]

        # 4. Retornar datos consolidados (Ruta Feliz)
        return {
            "mensaje": "Consulta de saldos exitosa",
            "fecha_proceso": datetime.now(),
            "capital_total": capital_total,
            "intereses_causados": capital_total * 0.05, 
            "intereses_contingentes": 0.0,
            "detalle_facturas": detalle_facturas_pydantic,
            "success": True
        }