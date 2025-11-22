# app/repository/pagos_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.database import FacturaDB, PagoDB, PacienteDB
from app.schemas.pago_schemas import IPagoRequest
from typing import List, Dict, Any

class PagosRepository:
    def __init__(self, db: Session):
        self.db = db

    # === HU-1 Métodos (READ) ===
    def obtener_facturas_pendientes_por_paciente(self, id_paciente: int) -> List[FacturaDB] | None:
        paciente_existe = self.db.get(PacienteDB, id_paciente)
        if not paciente_existe:
            return None 

        stmt = select(FacturaDB).where(
            (FacturaDB.id_paciente == id_paciente) & 
            (FacturaDB.estado_factura == 'Pendiente')
        )
        return self.db.scalars(stmt).all()

    # === HU-2 Métodos (VALIDATE / WRITE) ===
    def verificar_factura_pendiente(self, id_factura: int) -> bool:
        stmt = select(FacturaDB.estado_factura).where(FacturaDB.id_factura == id_factura)
        estado = self.db.scalar(stmt)
        return estado == 'Pendiente'
    
    def crear_registro_pago(self, data: IPagoRequest, transaccion_id: str, estado: str) -> int:
        nuevo_pago = PagoDB(
            id_factura=data.id_factura,
            monto_pagado=data.monto_pago,
            estado_pago=estado,
            transaccion_bancaria_id=transaccion_id
        )
        self.db.add(nuevo_pago)
        self.db.commit()
        self.db.refresh(nuevo_pago)
        return nuevo_pago.id_pago
    
    # === HU-5 Métodos (READ / UPDATE) ===
    def obtener_pago_por_id(self, id_pago: int) -> PagoDB | None:
        return self.db.get(PagoDB, id_pago)

    def actualizar_estado_pago(self, id_pago: int, nuevo_estado: str) -> PagoDB:
        # 1. Actualiza el estado del Pago
        stmt_pago = update(PagoDB).where(PagoDB.id_pago == id_pago).values(estado_pago=nuevo_estado)
        self.db.execute(stmt_pago)
        
        # 2. Si el pago fue exitoso, actualiza el estado de la Factura
        if nuevo_estado == 'Pagado':
            pago_obj = self.db.get(PagoDB, id_pago)
            if pago_obj:
                stmt_factura = update(FacturaDB).where(FacturaDB.id_factura == pago_obj.id_factura).values(estado_factura='Pagada')
                self.db.execute(stmt_factura)
        
        self.db.commit()
        return self.db.get(PagoDB, id_pago)

    # === HU-6 Métodos (READ) ===
    def obtener_datos_paciente_por_pago(self, id_pago: int) -> Dict[str, Any] | None:
        """Obtiene datos de contacto del paciente relacionados con el pago (HU-6)."""
        
        stmt = select(
            PacienteDB.email, PacienteDB.nombre_completo, PagoDB.estado_pago
        ).join(
            FacturaDB, PagoDB.id_factura == FacturaDB.id_factura
        ).join(
            PacienteDB, FacturaDB.id_paciente == PacienteDB.id_paciente
        ).where(PagoDB.id_pago == id_pago)
        
        resultado = self.db.execute(stmt).first()
        if resultado:
            return {
                "email": resultado[0],
                "nombre": resultado[1],
                "estado_final": resultado[2]
            }
        return None