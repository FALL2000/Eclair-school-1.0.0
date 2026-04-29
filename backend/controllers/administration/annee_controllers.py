from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from schemas.administration.annee_dto import AnneeCreateDTO, AnneeResponseDTO, AnneeUpdateDTO
from repositories.administration.annee_repository import AnneeRepository
from services.administration.annee_service import AnneeService
from common.dependencies import check_permission_user, get_db


router = APIRouter()


def get_annee_service(db: Session = Depends(get_db)):
    annee_repo = AnneeRepository(db)
    return AnneeService(annee_repo)


@router.post(
    "/add",
    summary="Definir une annee scolaire",
    status_code=201,
    response_model=AnneeResponseDTO
)
def add_annee(
    annee_in: AnneeCreateDTO,
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)]
):
    """
    Les codes de response:
    201: Annee enregistre avec succes
    400-422: Mauvaise requete(format de donnee invalide, donnees ne respectant le format attendu)
    403: user ne dispose pas les droits pour l'action
    409: duplication de code(annee existant)
    500: Erreur interne au serveur
    """
    return annee_service.define_annee_scolaire(annee_in)


@router.patch(
    "/update/{annee_id}",
    summary="Modifier une annee scolaire",
    status_code=201,
    response_model=AnneeResponseDTO
)
def update_annee(
    annee_id: int,
    annee_update: AnneeUpdateDTO,
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)]
):
    """
    Les codes de response:
    200: Annee enregistre avec succes
    400-422: Mauvaise requete(format de donnee invalide, donnees ne respectant le format attendu)
    403: user ne dispose pas les droits pour l'action
    404: Annee non trouve en BD
    409: Impossible de modifier l'annee car ayant des inscriptions
    500: Erreur interne au serveur
    """
    return annee_service.update_annee_scolaire(annee_update, annee_id)
