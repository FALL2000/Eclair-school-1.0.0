from fastapi import APIRouter
from controllers.eleve.eleve_controllers import router as eleve_router

router = APIRouter()


def include_api_routes() -> APIRouter:
    """Enregistre tous les sous-routeurs sur le routeur principal."""
    router.include_router(eleve_router, prefix="/eleves", tags=["eleves"])

    return router


include_api_routes()
