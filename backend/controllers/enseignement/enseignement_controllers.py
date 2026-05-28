from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.enseignants.enseignant_repository import EnseignantRepository
from repositories.enseignement.enseignement_repository import EnseignementRepository
from schemas.enseignement.enseignement_dto import (
    EnseignantAvecEnseignementsBulkCreateDTO,
    EnseignantAvecEnseignementsResponseDTO,
    EnseignementAvecEnseignantCreateDTO,
    EnseignementAvecEnseignantResponseDTO,
    EnseignementBulkDeleteDTO,
    EnseignementBulkUpdateDTO,
    EnseignementResponseDTO,
    EnseignementSansEnseignantBulkCreateDTO,
    EnseignementUpdateDTO,
)
from services.enseignement.enseignement_service import EnseignementService

router = APIRouter()


def get_enseignement_service(db: Session = Depends(get_db)):
    enseignement_repo = EnseignementRepository(db)
    enseignant_repo = EnseignantRepository(db)
    return EnseignementService(enseignement_repo, enseignant_repo)


@router.post(
    "/add",
    summary="Ajouter un enseignement avec création de l'enseignant",
    status_code=201,
    response_model=EnseignementAvecEnseignantResponseDTO,
)
def add_enseignement(
    data: EnseignementAvecEnseignantCreateDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_type_salaire: Annotated[int, Query(description="Id du type de salaire de l'enseignant")] = ...,
    id_matiere: Annotated[int, Query(description="Id de la matière enseignée")] = ...,
):
    return enseignement_service.add_enseignement(data, id_type_salaire, id_matiere)


@router.post(
    "/add-bulk-with-enseignant",
    summary="Ajouter un enseignant avec plusieurs de ses enseignements en masse",
    status_code=201,
    response_model=EnseignantAvecEnseignementsResponseDTO,
)
def add_bulk_with_enseignant(
    data: EnseignantAvecEnseignementsBulkCreateDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_type_salaire: Annotated[int, Query(description="Id du type de salaire de l'enseignant")] = ...,
):
    return enseignement_service.add_bulk_with_enseignant(data, id_type_salaire)


@router.post(
    "/add-bulk-without-enseignant",
    summary="Ajouter plusieurs enseignements en masse pour des enseignants existants",
    status_code=201,
    response_model=list[EnseignementResponseDTO],
)
def add_bulk_without_enseignant(
    data: EnseignementSansEnseignantBulkCreateDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_enseignant: Annotated[int, Query(description="Id de l'enseignant")] = ...,
):
    return enseignement_service.add_bulk_without_enseignant(data, id_enseignant)


@router.patch(
    "/update/{enseignement_id}",
    summary="Modifier un enseignement",
    status_code=200,
    response_model=EnseignementResponseDTO,
)
def update_enseignement(
    enseignement_id: int,
    data: EnseignementUpdateDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignement_service.update_enseignement(enseignement_id, data)


@router.patch(
    "/update-bulk",
    summary="Modifier plusieurs enseignements en masse",
    status_code=200,
    response_model=list[EnseignementResponseDTO],
)
def update_bulk_enseignements(
    data: EnseignementBulkUpdateDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignement_service.update_bulk_enseignements(data)


@router.delete(
    "/delete/{enseignement_id}",
    summary="Supprimer un enseignement",
    status_code=200,
)
def delete_enseignement(
    enseignement_id: int,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignement_service.delete_enseignement(enseignement_id)


@router.delete(
    "/delete-bulk",
    summary="Supprimer plusieurs enseignements en masse",
    status_code=200,
)
def delete_bulk_enseignements(
    data: EnseignementBulkDeleteDTO,
    enseignement_service: Annotated[EnseignementService, Depends(get_enseignement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return enseignement_service.delete_bulk_enseignements(data)
