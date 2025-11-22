# main.py

# 📦 Importaciones estándar y de terceros
import os
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse



# ----------------------------------------------------
# 🔐 Cargar variables de entorno (Mantener)
load_dotenv()
secret_key = os.getenv("SECRET_KEY")
db_url = os.getenv("DATABASE_URL")
# ----------------------------------------------------

# 🚀 Instancia de FastAPI (Actualizar metadatos y mantener la instancia)
app = FastAPI(
    # Metadatos actualizados para reflejar el proyecto de pagos
    title="API de Gestión de Pagos Odontológicos",
    description="Implementación de Historias de Usuario (HU-1, HU-2, HU-5, HU-6) con arquitectura en capas.",
    version="1.0.0"
)

# ----------------------------------------------------


# 🏠 Ruta raíz (Mantener)
@app.get("/", tags=["Infraestructura"])
async def root():
    """
    Endpoint de bienvenida.
    """
    return {
        "message": "Web Service de Gestión de Pagos funcionando correctamente.",
        "status": "online",
        "version": "1.0.0"
    }

# 📦 Endpoint con parámetros (Mantener como ejemplo)
@app.get("/items/{item_id}", tags=["Ejemplos"])
async def read_item(item_id: int, q: str = None):
    """
    Ejemplo con parámetros de ruta y query.
    """
    return {
        "item_id": item_id,
        "query": q,
        "note": "Este es un endpoint de ejemplo de la estructura base."
    }

# ❤️ Health check (Mantener)
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Infraestructura"])
async def health_check():
    """
    Verifica el estado del servidor.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )