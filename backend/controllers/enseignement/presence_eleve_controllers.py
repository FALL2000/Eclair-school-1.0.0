from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.enseignement.presence_eleve_repository import PresenceEleveRepository
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_eleve_dto import (
    PresenceEleveBulkCreateDTO,
    PresenceEleveBulkUpdateDTO,
    PresenceEleveResponseDTO,
    PresenceEleveWithEleveResponseDTO,
)
from services.enseignement.presence_eleve_service import PresenceEleveService

router = APIRouter()


def get_presence_eleve_service(db: Session = Depends(get_db)):
    presence_eleve_repo = PresenceEleveRepository(db)
    presence_enseignant_repo = PresenceEnseignantRepository(db)
    configuration_repo = ConfigurationRepository(db)
    return PresenceEleveService(presence_eleve_repo, presence_enseignant_repo, configuration_repo)


@router.get(
    "/list",
    summary="Récupérer les présences des élèves par cours et/ou date avec infos élève",
    status_code=200,
    response_model=list[PresenceEleveWithEleveResponseDTO],
)
def get_presences_eleves(
    presence_eleve_service: Annotated[PresenceEleveService, Depends(get_presence_eleve_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_cours: Annotated[Optional[int], Query(description="Id du cours")] = None,
    date_cours: Annotated[Optional[date], Query(description="Date du cours")] = None,
):
    return presence_eleve_service.get_presences_by_filters(id_cours, date_cours)


@router.post(
    "/add-bulk",
    summary="Ajouter en masse les présences des élèves",
    status_code=201,
    response_model=list[PresenceEleveResponseDTO],
)
def add_bulk_presences_eleves(
    data: PresenceEleveBulkCreateDTO,
    presence_eleve_service: Annotated[PresenceEleveService, Depends(get_presence_eleve_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return presence_eleve_service.add_bulk_presences_eleves(data)


@router.patch(
    "/update-bulk",
    summary="Modifier en masse les présences des élèves",
    status_code=200,
    response_model=list[PresenceEleveResponseDTO],
)
def update_bulk_presences_eleves(
    data: PresenceEleveBulkUpdateDTO,
    presence_eleve_service: Annotated[PresenceEleveService, Depends(get_presence_eleve_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return presence_eleve_service.update_bulk_presences_eleves(data)
