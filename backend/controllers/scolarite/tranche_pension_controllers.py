from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.scolarite.tranche_pension_repository import TranchePensionRepository
from schemas.scolarite.tranche_pension_dto import (
    TranchePensionBulkCreateDTO,
    TranchePensionBulkUpdateDTO,
    TranchePensionCreateDTO,
    TranchePensionResponseDTO,
    TranchePensionUpdateDTO,
)
from services.scolarite.tranche_pension_service import TranchePensionService

router = APIRouter()


def get_tranche_service(db: Session = Depends(get_db)):
    tranche_repo = TranchePensionRepository(db)
    return TranchePensionService(tranche_repo)


@router.get(
    "/all",
    summary="Recuperer toutes les tranches pension",
    status_code=200,
    response_model=list[TranchePensionResponseDTO],
)
def get_all_tranches(
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.get_all_tranches()


@router.get(
    "/by-niveau/{id_niveau}",
    summary="Recuperer les tranches pension d'un niveau",
    status_code=200,
    response_model=list[TranchePensionResponseDTO],
)
def get_tranches_by_niveau(
    id_niveau: int,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.get_tranches_by_niveau(id_niveau)


@router.get(
    "/one/{tranche_id}",
    summary="Recuperer une tranche pension",
    status_code=200,
    response_model=TranchePensionResponseDTO,
)
def get_one_tranche(
    tranche_id: int,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.get_one_tranche(tranche_id)


@router.post(
    "/add",
    summary="Ajouter une tranche pension",
    status_code=201,
    response_model=TranchePensionResponseDTO,
)
def add_tranche(
    tranche_in: TranchePensionCreateDTO,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_niveau: Annotated[int, Query(description="Id du niveau auquel appartient la tranche")] = ...,
):
    return tranche_service.add_tranche(tranche_in, id_niveau)


@router.post(
    "/add-bulk",
    summary="Ajouter plusieurs tranches pension en masse pour un niveau",
    status_code=201,
    response_model=list[TranchePensionResponseDTO],
)
def add_bulk_tranches(
    data: TranchePensionBulkCreateDTO,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_niveau: Annotated[int, Query(description="Id du niveau auquel appartiennent les tranches")] = ...,
):
    return tranche_service.add_bulk_tranches(data, id_niveau)


@router.patch(
    "/update/{tranche_id}",
    summary="Modifier une tranche pension",
    status_code=200,
    response_model=TranchePensionResponseDTO,
)
def update_tranche(
    tranche_id: int,
    tranche_update: TranchePensionUpdateDTO,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.update_tranche(tranche_id, tranche_update)


@router.patch(
    "/update-bulk",
    summary="Modifier plusieurs tranches pension en masse",
    status_code=200,
    response_model=list[TranchePensionResponseDTO],
)
def update_bulk_tranches(
    data: TranchePensionBulkUpdateDTO,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.update_bulk_tranches(data)


@router.delete(
    "/delete/{tranche_id}",
    summary="Supprimer une tranche pension",
    status_code=200,
)
def delete_tranche(
    tranche_id: int,
    tranche_service: Annotated[TranchePensionService, Depends(get_tranche_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return tranche_service.delete_tranche(tranche_id)
