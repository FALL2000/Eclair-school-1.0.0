from fastapi import APIRouter
from controllers.eleve.eleve_controllers import router as eleve_router
from controllers.administration.user_controllers import router as user_router
from controllers.administration.appreciation_controllers import router as appreciation_router
from controllers.administration.classe_controllers import router as classe_router
from controllers.administration.cycle_controllers import router as cycle_router
from controllers.administration.groupe_matiere_controllers import router as groupe_matiere_router
from controllers.administration.groupe_matiere_evalue_controllers import router as groupe_matiere_evalue_router
from controllers.administration.matiere_controllers import router as matiere_router
from controllers.administration.matiere_evalue_controllers import router as matiere_evalue_router
from controllers.administration.niveau_controllers import router as niveau_router
from controllers.administration.section_controllers import router as section_router
from controllers.administration.serie_controllers import router as serie_router
from controllers.administration.trimestre_controllers import router as trimestre_router
from controllers.authentication.auth_controllers import router as auth_router
from controllers.administration.annee_controllers import router as annee_router

router = APIRouter()


def include_api_routes() -> APIRouter:
    """Enregistre tous les sous-routeurs sur le routeur principal."""
    router.include_router(eleve_router, prefix="/eleves", tags=["eleves"])
    router.include_router(user_router, prefix="/user", tags=["users"])
    router.include_router(auth_router, prefix="/auth", tags=["authentication"])
    router.include_router(annee_router, prefix="/annee", tags=["annees"])
    router.include_router(appreciation_router, prefix="/appreciation", tags=["appreciations"])
    router.include_router(section_router, prefix="/section", tags=["sections"])
    router.include_router(serie_router, prefix="/serie", tags=["series"])
    router.include_router(cycle_router, prefix="/cycle", tags=["cycles"])
    router.include_router(niveau_router, prefix="/niveau", tags=["niveaux"])
    router.include_router(classe_router, prefix="/classe", tags=["classes"])
    router.include_router(trimestre_router, prefix="/trimestre", tags=["trimestres"])
    router.include_router(groupe_matiere_router, prefix="/groupe-matiere", tags=["groupe matieres"])
    router.include_router(matiere_router, prefix="/matiere", tags=["matieres"])
    router.include_router(groupe_matiere_evalue_router, prefix="/groupe-matiere-evalue", tags=["groupe matieres evalues"])
    router.include_router(matiere_evalue_router, prefix="/matiere-evalue", tags=["matieres evaluees"])

    return router


include_api_routes()
