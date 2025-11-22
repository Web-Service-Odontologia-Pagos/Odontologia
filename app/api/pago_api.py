# app/api/pago_api.py

from fastapi import APIRouter, status, Depends, Path
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.schemas.pago_schemas import (
    IPagoRequest, IPagoResponse, CambioEPRequest, CambioEPResponse
)
from app.services.transaccion_service import TransaccionService
from app.database import get_db

router = APIRouter(prefix="/pago")

def get_transaccion_service(db: Session = Depends(get_db)):
    return TransaccionService(db)

# --- ENDPOINT HU-2: IPago (Método POST) ---
@router.post(
    "/IPago/datosP",
    response_model=IPagoResponse,
    status_code=status.HTTP_200_OK,
    summary="HU-2: Iniciar el proceso de pago con datos de tarjeta."
)
def iniciar_pago_endpoint(
    request_data: IPagoRequest, 
    service: TransaccionService = Depends(get_transaccion_service)
):
    try:
        resultado = service.iniciar_pago(request_data)
        
        return IPagoResponse(
            mensaje="Se inició el proceso de pago y se registró en estado 'En Proceso'.",
            **resultado,
            success=True
        )
    except HTTPException as e:
        raise e

# --- ENDPOINT HU-5: CambioEP (Método PUT, encadena a HU-6) ---
@router.put(
    "/{id_paciente}/cambioEP",
    response_model=CambioEPResponse,
    status_code=status.HTTP_200_OK,
    summary="HU-5: Actualizar el estado final del pago en la base de datos (y dispara HU-6)."
)
def cambiar_estado_pago_endpoint(
    id_paciente: int, # Ruta de diseño
    request_data: CambioEPRequest,
    service: TransaccionService = Depends(get_transaccion_service)
):
    try:
        pago_actualizado = service.cambiar_estado_pago(request_data)

        return CambioEPResponse(
            mensaje="El estado de pago fue actualizado correctamente en la base de datos.",
            data=pago_actualizado,
            success=True
        )
    except HTTPException as e:
        raise e