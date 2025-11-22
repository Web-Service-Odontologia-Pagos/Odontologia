# app/api/paciente_api.py

from fastapi import APIRouter, status, Depends, Path
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.schemas.pago_schemas import ConsultaFResponse
# Asumo que el servicio de consulta se encuentra en el archivo anterior, lo importamos como ConsultaService
from app.services.consulta_service import ConsultaService 
from app.database import get_db # Importamos la función de dependencia de la BD

router = APIRouter(prefix="/usuarios")

# Función de dependencia para inyectar el Service, el cual a su vez recibe la sesión de BD
def get_consulta_service(db: Session = Depends(get_db)):
    return ConsultaService(db)

# --- ENDPOINT HU-1: ConsultaF (Método GET) ---
@router.get(
    "/{id_paciente}/consultaF",
    response_model=ConsultaFResponse, # El modelo de salida Pydantic
    status_code=status.HTTP_200_OK,
    summary="HU-1: Consulta de todas las facturas pendientes de un paciente."
)
def consulta_facturas_endpoint(
    id_paciente: int = Path(..., description="ID del paciente a consultar."),
    service: ConsultaService = Depends(get_consulta_service) # Inyección del servicio
):
    """
    Retorna la lista consolidada de facturas pendientes para un paciente.
    """
    try:
        datos_consolidados = service.consultar_facturas_pendientes(id_paciente)
        
        # Mapea el diccionario retornado por el Service al modelo Pydantic final
        return ConsultaFResponse.model_validate(datos_consolidados)

    except HTTPException as e:
        # Captura 404/400/502 lanzados desde la capa de servicio
        raise e
    except Exception:
        # Manejo de error 503 (ej. fallo de conexión a la BD)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail={"mensaje": "No fue posible consultar los saldos consolidados.", "success": False}
        )