from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_enseignant_dto import (
    PresenceEnseignantCreateDTO,
    PresenceEnseignantResponseDTO,
    PresenceEnseignantUpdateDTO,
)
from services.enseignement.presence_enseignant_service import PresenceEnseignantService

router = APIRouter()


def get_presence_enseignant_service(db: Session = Depends(get_db)):
    presence_enseignant_repo = PresenceEnseignantRepository(db)
    return PresenceEnseignantService(presence_enseignant_repo)


@router.get(
    "/list",
    summary="Récupérer les présences enseignants par cours et/ou date",
    status_code=200,
    response_model=list[PresenceEnseignantResponseDTO],
)
def get_presences_enseignant(
    presence_enseignant_service: Annotated[PresenceEnseignantService, Depends(get_presence_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return presence_enseignant_service.update_presence_enseignant(presence_id, data)
