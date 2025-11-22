# app/services/transaccion_service.py

from app.schemas.pago_schemas import IPagoRequest, CambioEPRequest, PagoBase, FacturaDetalle
from app.repository.pagos_repository import PagosRepository
from app.external.soap_client import SOAPClient
from app.external.notificacion_client import NotificacionClient
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

class BaseService:
    def __init__(self, db: Session):
        self.repo = PagosRepository(db)

class TransaccionService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.soap_client = SOAPClient()
        self.notif_client = NotificacionClient() 
    
    # === HU-1: ConsultaF ===
    def consultar_facturas_pendientes(self, id_paciente: int) -> Dict[str, Any]:
        facturas_db_data = self.repo.obtener_facturas_pendientes_por_paciente(id_paciente)

        if facturas_db_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"mensaje": "ID de paciente inválido.", "success": False})
        
        if not facturas_db_data:
             return {
                "mensaje": "No existen saldos consolidados para el paciente.",
                "fecha_proceso": datetime.now(),
                "capital_total": 0.0, "intereses_causados": 0.0, "intereses_contingentes": 0.0,
                "detalle_facturas": [], "success": False
            }

        capital_total = sum(f.monto_total for f in facturas_db_data)
        detalle_facturas_pydantic = [FacturaDetalle.model_validate(f) for f in facturas_db_data]

        return {
            "mensaje": "Consulta de saldos exitosa",
            "fecha_proceso": datetime.now(),
            "capital_total": capital_total,
            "intereses_causados": capital_total * 0.05,
            "intereses_contingentes": 0.0,
            "detalle_facturas": detalle_facturas_pydantic,
            "success": True
        }

    # === HU-2: IPago ===
    def iniciar_pago(self, data: IPagoRequest) -> Dict[str, Any]:
        if not self.repo.verificar_factura_pendiente(data.id_factura):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"mensaje": "Factura no existe o ya ha sido pagada.", "success": False})

        # Encadenamiento a Servicio Externo (HU-3: EnvioP)
        try:
            respuesta_banco = self.soap_client.enviar_pago_al_banco(data)
            transaccion_id = respuesta_banco['transaccion_id']

            # Registrar pago en estado 'En Proceso'
            self.repo.crear_registro_pago(data, transaccion_id, estado="En Proceso")
            
            return {
                "id_factura": data.id_factura,
                "transaccion_id": transaccion_id,
                "estado_transaccion": "En Proceso"
            }

        except ConnectionError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail={"mensaje": "Error de comunicación con la entidad bancaria externa.", "success": False})

    # === HU-5: CambioEP (y encadenamiento a HU-6: NotificaciónP) ===
    def cambiar_estado_pago(self, data: CambioEPRequest) -> PagoBase:
        
        pago_existente = self.repo.obtener_pago_por_id(data.id_pago)
        if not pago_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"mensaje": f"No se encontró el registro de pago con ID: {data.id_pago}", "success": False})

        # 1. Operación de Actualización (HU-5)
        pago_actualizado = self.repo.actualizar_estado_pago(data.id_pago, data.estado)
        
        # 2. Obtener datos de Paciente (HU-6)
        datos_paciente = self.repo.obtener_datos_paciente_por_pago(data.id_pago)
        
        # 3. Encadenamiento a Notificación (HU-6: NotificaciónP)
        if datos_paciente:
            self.notif_client.enviar_notificacion(datos_paciente)
        
        return PagoBase.model_validate(pago_actualizado)