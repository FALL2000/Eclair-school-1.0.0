from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends
from sqlmodel import Session

from schemas.administration.annee_dto import AnneeCreateDTO, AnneeResponseDTO, AnneeUpdateDTO
from repositories.administration.annee_repository import AnneeRepository
from services.administration.annee_service import AnneeService
from common.dependencies import get_db, require_permission
from common.permissions import Action, Module


router = APIRouter()


def get_annee_service(db: Session = Depends(get_db)):
    annee_repo = AnneeRepository(db)
    return AnneeService(annee_repo)


@router.post(
    "/add",
    summary="Definir la premiere annee scolaire ou passer a l'annee suivante",
    status_code=201,
    response_model=AnneeResponseDTO
)
def add_annee(
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ANNEE, Action.AJOUTER))],
    annee_in: Annotated[AnneeCreateDTO | None, Body(
        description="Obligatoire uniquement pour la premiere annee du systeme ; ignore ensuite")] = None,
):
    """
    - Aucune annee en BD : cree la premiere annee avec le code (AAAA-AAAA) et le libelle fournis.
    - Sinon : l'annee en cours doit etre cloturee ; la nouvelle annee est calculee a partir de la plus
      recente (2026-2027 -> 2027-2028) et le corps de la requete est ignore.

    Les codes de response:
    201: Annee enregistre avec succes
    400: Premiere annee sans code ni libelle (PREMIERE_ANNEE_REQUISE)
    422: Code ne respectant pas le format AAAA-AAAA
    403: user ne dispose pas les droits pour l'action
    409: duplication de code, annee en cours non cloturee (ANNEE_EN_COURS)
         ou annee suivante impossible a calculer (CALCUL_ANNEE_IMPOSSIBLE)
    500: Erreur interne au serveur
    """
    return annee_service.define_annee_scolaire(annee_in)


@router.patch(
    "/update/{annee_id}",
    summary="Modifier ou cloturer une annee scolaire",
    status_code=201,
    response_model=AnneeResponseDTO
)
def update_annee(
    annee_id: int,
    annee_update: AnneeUpdateDTO,
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ANNEE, Action.MODIFIER))]
):
    """
    Les codes de response:
    200: Annee enregistre avec succes
    400-422: Mauvaise requete(format de donnee invalide, donnees ne respectant le format attendu)
    403: user ne dispose pas les droits pour l'action
    404: Annee non trouve en BD
    409: Code ou libelle non modifiable car l'annee a des inscriptions (INSCRIPTIONS_IN_ANNEE),
         ou tentative de rouvrir une annee cloturee (ANNEE_CLOTUREE)
    Pour cloturer l'annee en cours : {"is_cloture": true}
    500: Erreur interne au serveur
    """
    return annee_service.update_annee_scolaire(annee_update, annee_id)


@router.get(
    "/annee-scolaire",
    summary="Recupere l'annee scolaire en cours",
    status_code=201,
    response_model=AnneeResponseDTO
)
def get_annee_scolaire(
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ANNEE, Action.CONSULTER))]
):
    annee_scolaire = annee_service.get_annee_scolaire()
    return annee_scolaire[0]


@router.get(
    "/all",
    summary="Recupere toutes les annees scolaires (de la plus recente a la plus ancienne)",
    status_code=200,
    response_model=list[AnneeResponseDTO]
)
def get_all_annees(
    annee_service: Annotated[AnneeService, Depends(get_annee_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ANNEE, Action.CONSULTER))]
):
    return annee_service.get_all_annees()
