from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignants.enseignant_repository import EnseignantRepository
from schemas.enseignants.enseignant_dto import (
    EnseignantBulkUpdateDTO,
    EnseignantDetailResponseDTO,
    EnseignantResponseDTO,
    EnseignantUpdateDTO,
    PaginatedEnseignant,
)
from services.enseignants.enseignant_service import EnseignantService

router = APIRouter()


def get_enseignant_service(db: Session = Depends(get_db)):
    enseignant_repo = EnseignantRepository(db)
    annee_repo = AnneeRepository(db)
    return EnseignantService(enseignant_repo, annee_repo)


@router.get(
    "/all",
    summary="Récupérer tous les enseignants avec pagination",
    status_code=200,
    response_model=PaginatedEnseignant,
)
def get_all_enseignants(
    enseignant_service: Annotated[EnseignantService, Depends(get_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    page: Annotated[int | None, Query(description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(description="Nombre d'éléments par page")] = None,
):
    return enseignant_service.get_all_enseignants(page, page_size)


@router.get(
    "/one/{enseignant_id}",
    summary="Récupérer un enseignant avec ses enseignements",
    status_code=200,
    response_model=EnseignantDetailResponseDTO,
)
def get_one_enseignant(
    enseignant_id: int,
    enseignant_service: Annotated[EnseignantService, Depends(get_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignant_service.get_one_enseignant(enseignant_id)


@router.patch(
    "/update/{enseignant_id}",
    summary="Modifier un enseignant",
    status_code=200,
    response_model=EnseignantResponseDTO,
)
def update_enseignant(
    enseignant_id: int,
    data: EnseignantUpdateDTO,
    enseignant_service: Annotated[EnseignantService, Depends(get_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignant_service.update_enseignant(enseignant_id, data)


@router.patch(
    "/update-bulk",
    summary="Modifier plusieurs enseignants en masse",
    status_code=200,
    response_model=list[EnseignantResponseDTO],
)
def update_bulk_enseignants(
    data: EnseignantBulkUpdateDTO,
    enseignant_service: Annotated[EnseignantService, Depends(get_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignant_service.update_bulk_enseignants(data)


@router.delete(
    "/delete/{enseignant_id}",
    summary="Supprimer un enseignant (impossible durant une année en cours)",
    status_code=200,
)
def delete_enseignant(
    enseignant_id: int,
    enseignant_service: Annotated[EnseignantService, Depends(get_enseignant_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignant_service.delete_enseignant(enseignant_id)
