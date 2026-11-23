from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_db
from repositories.administration.etablissement_repository import EtablissementRepository
from schemas.administration.etablissement_dto import EtablissementResponseDTO
from services.administration.etablissement_service import EtablissementService

router = APIRouter()


def get_etablissement_service(db: Session = Depends(get_db)):
    etablissement_repo = EtablissementRepository(db)
    return EtablissementService(etablissement_repo)


@router.get(
    "",
    summary="Recupere les informations de l'etablissement",
    status_code=200,
    response_model=EtablissementResponseDTO,
)
def get_etablissement(
    etablissement_service: Annotated[EtablissementService, Depends(get_etablissement_service)],
):
    """
    Informations de l'etablissement (la table ne contient qu'une ligne).
    Sans authentification : elles sont affichees sur la page de connexion.
    404: ETABLISSEMENT_NOT_FOUND si l'etablissement n'est pas encore renseigne
    """
    return etablissement_service.get_etablissement()
