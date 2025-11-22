# app/external/soap_client.py (Simulación HU-3: EnvioP)

from app.schemas.pago_schemas import IPagoRequest
from typing import Dict
from datetime import datetime

class SOAPClient:
    """Simula el envío de datos de pago al banco."""
    def enviar_pago_al_banco(self, data: IPagoRequest) -> Dict[str, str]:
        # Simulación de éxito
        return {
            'status': 'OK',
            'transaccion_id': f"TXN-{data.id_factura}-{datetime.now().microsecond}"
        }

# app/external/notificacion_client.py (Simulación HU-6: NotificaciónP)

from typing import Dict, Any

class NotificacionClient:
    """Simula la llamada al servicio de envío de correos/SMS."""
    def enviar_notificacion(self, datos_paciente: Dict[str, Any]):
        print(f"DEBUG HU-6: Notificación enviada a {datos_paciente['email']} por estado: {datos_paciente['estado_final']}")
        return {"success": True}