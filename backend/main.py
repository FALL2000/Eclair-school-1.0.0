from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from controllers.router import router as api_router
from utils.logger import get_logger
from config.settings import get_settings

logger = get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Gère le cycle de vie de l’application (démarrage puis arrêt du serveur)."""
    logger.info("Application FastAPI démarrée (lifespan startup)")
    print("Application FastAPI démarrée (lifespan startup)")
    yield
    logger.info("Application FastAPI arrêtée (lifespan shutdown)")
    print("Application FastAPI arrêtée (lifespan shutdown)")


def init_api() -> FastAPI:
    logger.info("L'application démarre")

    application = FastAPI(title="Eclair School API", lifespan=lifespan)

    application.include_router(api_router, prefix=settings.api_prefix)

    # Allow cors
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = init_api()


@app.get("/ping")
def ping_route():
    """Route pour vérifier que fast api fonctionne"""
    return {"status": "success", "message": "Le serveur FastAPI tourne !"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler_app(request: Request, exceptions: RequestValidationError):
    """Gestion des erreurs retournes par les validateurs pydantic"""
    error_messages = []
    for error in exceptions.errors():
        error_messages.append({
            "location": error["loc"],
            "message": error["msg"]
        })
    return JSONResponse(status_code=400, content={"detail": error_messages})


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host=settings.host_ip,
        port=8000,
        reload=settings.debug,
    )
