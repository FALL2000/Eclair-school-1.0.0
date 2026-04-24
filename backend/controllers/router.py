from fastapi import APIRouter
from controllers.eleve.eleve_controllers import router as eleve_router
from controllers.administration.user_controllers import router as user_router
from controllers.authentication.auth_controllers import router as auth_router

router = APIRouter()


def include_api_routes() -> APIRouter:
    """Enregistre tous les sous-routeurs sur le routeur principal."""
    router.include_router(eleve_router, prefix="/eleves", tags=["eleves"])
    router.include_router(user_router, prefix="/user", tags=["users"])
    router.include_router(auth_router, prefix="/auth", tags=["authentication"])

    return router


include_api_routes()
