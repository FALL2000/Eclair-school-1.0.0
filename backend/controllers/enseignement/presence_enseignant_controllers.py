from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_enseignant_dto import (
    PresenceEnseignantCreateDTO,
    PresenceEnseignantResponseDTO,
    PresenceEnseignantUpdateDTO,
    PresencesJourDTO,
    PresencesJourSaveDTO,
)
from services.enseignement.presence_enseignant_service import PresenceEnseignantService

router = APIRouter()


def get_presence_enseignant_service(db: Session = Depends(get_db)):
    presence_enseignant_repo = PresenceEnseignantRepository(db)
    return PresenceEnseignantService(presence_enseignant_repo, AnneeRepository(db))


@router.get(
    "/jour",
    summary="Cours d'une date (toutes classes, ou une classe) avec la présence de leur enseignant",
    status_code=200,
    response_model=PresencesJourDTO,
)
def get_presences_jour(
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.PRESENCE_ENSEIGNANT, Action.CONSULTER))],
    date_cours: Annotated[date, Query(description="Date des cours")] = ...,
    q: Annotated[Optional[str], Query(max_length=100, description="Nom ou prénom de l'enseignant")] = None,
    id_enseignant: Annotated[Optional[int], Query(description="Id de l'enseignant")] = None,
    id_classe: Annotated[Optional[int], Query(description="Id de la classe (vide : toutes les classes)")] = None,
):
    return presence_enseignant_service.get_presences_jour(date_cours, q, id_enseignant, id_classe)


@router.post(
    "/jour",
    summary="Enregistrer la présence des enseignants pour les cours d'une date (mise à jour avec presence_enseignant:modifier)",
    status_code=200,
    response_model=PresencesJourDTO,
)
def enregistrer_presences_jour(
    data: PresencesJourSaveDTO,
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.PRESENCE_ENSEIGNANT, Action.AJOUTER))],
):
    return presence_enseignant_service.enregistrer_presences_jour(data, current_user)


@router.get(
    "/list",
    summary="Récupérer les présences enseignants par cours et/ou date",
    status_code=200,
    response_model=list[PresenceEnseignantResponseDTO],
)
def get_presences_enseignant(
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.PRESENCE_ENSEIGNANT, Action.CONSULTER))],
    id_cours: Annotated[Optional[int], Query(description="Id du cours")] = None,
    date_cours: Annotated[Optional[date], Query(description="Date du cours")] = None,
):
    return presence_enseignant_service.get_presences_by_filters(id_cours, date_cours)


@router.post(
    "/add",
    summary="Ajouter une présence enseignant",
    status_code=201,
    response_model=PresenceEnseignantResponseDTO,
)
def add_presence_enseignant(
    data: PresenceEnseignantCreateDTO,
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.PRESENCE_ENSEIGNANT, Action.AJOUTER))],
    id_cours: Annotated[int, Query(description="Id du cours")] = ...,
    id_enseignant: Annotated[int, Query(description="Id de l'enseignant")] = ...,
):
    return presence_enseignant_service.add_presence_enseignant(data, id_cours, id_enseignant)


@router.patch(
    "/update/{presence_id}",
    summary="Modifier une présence enseignant",
    status_code=200,
    response_model=PresenceEnseignantResponseDTO,
)
def update_presence_enseignant(
    presence_id: int,
    data: PresenceEnseignantUpdateDTO,
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.PRESENCE_ENSEIGNANT, Action.MODIFIER))],
):
    return presence_enseignant_service.update_presence_enseignant(presence_id, data)
