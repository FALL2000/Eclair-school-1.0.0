from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.cycle_repository import CycleRepository
from schemas.administration.cycle_dto import CycleCreateDTO, CycleResponseDTO, CycleUpdateDTO
from services.administration.cycle_service import CycleService

router = APIRouter()


def get_cycle_service(db: Session = Depends(get_db)):
    cycle_repo = CycleRepository(db)
    annee_repo = AnneeRepository(db)
    return CycleService(cycle_repo, annee_repo)


@router.post(
    "/add/{section_id}",
    summary="Ajouter un cycle",
    status_code=201,
    response_model=CycleResponseDTO,
)
def add_cycle(
    section_id: int,
    cycle_in: CycleCreateDTO,
    cycle_service: Annotated[CycleService, Depends(get_cycle_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cycle_service.add_cycle(cycle_in, section_id)


@router.patch(
    "/update/{cycle_id}",
    summary="Modifier un cycle",
    status_code=200,
    response_model=CycleResponseDTO,
)
def update_cycle(
    cycle_id: int,
    cycle_update: CycleUpdateDTO,
    cycle_service: Annotated[CycleService, Depends(get_cycle_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cycle_service.update_cycle(cycle_update, cycle_id)


@router.delete(
    "/delete/{cycle_id}",
    summary="Supprimer un cycle",
    status_code=200,
)
def delete_cycle(
    cycle_id: int,
    cycle_service: Annotated[CycleService, Depends(get_cycle_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cycle_service.delete_cycle(cycle_id)


@router.get(
    "/{cycle_id}",
    summary="Recuperer un cycle",
    status_code=200,
    response_model=CycleResponseDTO,
)
def get_one_cycle(
    cycle_id: int,
    cycle_service: Annotated[CycleService, Depends(get_cycle_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cycle_service.get_one_cycle(cycle_id)


@router.get(
    "/all",
    summary="Recuperer tous les cycles",
    status_code=200,
    response_model=list[CycleResponseDTO],
)
def get_all_cycle(
    cycle_service: Annotated[CycleService, Depends(get_cycle_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cycle_service.get_all_cycle()
