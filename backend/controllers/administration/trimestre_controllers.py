from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.trimestre_repository import TrimestreRepository
from schemas.administration.trimestre_dto import (
    TrimestreCreateDTO,
    TrimestreResponseDTO,
    TrimestreUpdateDTO,
)
from services.administration.trimestre_service import TrimestreService

router = APIRouter()


def get_trimestre_service(db: Session = Depends(get_db)):
    trimestre_repo = TrimestreRepository(db)
    annee_repo = AnneeRepository(db)
    return TrimestreService(trimestre_repo, annee_repo)


@router.post(
    "/add",
    summary="Ajouter un trimestre",
    status_code=201,
    response_model=TrimestreResponseDTO,
)
def add_trimestre(
    trimestre_in: TrimestreCreateDTO,
    trimestre_service: Annotated[TrimestreService, Depends(get_trimestre_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return trimestre_service.add_trimestre(trimestre_in)


@router.patch(
    "/update/{trimestre_id}",
    summary="Modifier un trimestre",
    status_code=200,
    response_model=TrimestreResponseDTO,
)
def update_trimestre(
    trimestre_id: int,
    trimestre_update: TrimestreUpdateDTO,
    trimestre_service: Annotated[TrimestreService, Depends(get_trimestre_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return trimestre_service.update_trimestre(trimestre_update, trimestre_id)


@router.delete(
    "/delete/{trimestre_id}",
    summary="Supprimer un trimestre",
    status_code=200,
)
def delete_trimestre(
    trimestre_id: int,
    trimestre_service: Annotated[TrimestreService, Depends(get_trimestre_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return trimestre_service.delete_trimestre(trimestre_id)


@router.get(
    "/{trimestre_id}",
    summary="Recuperer un trimestre",
    status_code=200,
    response_model=TrimestreResponseDTO,
)
def get_one_trimestre(
    trimestre_id: int,
    trimestre_service: Annotated[TrimestreService, Depends(get_trimestre_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return trimestre_service.get_one_trimestre(trimestre_id)


@router.get(
    "/all",
    summary="Recuperer tous les trimestres",
    status_code=200,
    response_model=list[TrimestreResponseDTO],
)
def get_all_trimestre(
    trimestre_service: Annotated[TrimestreService, Depends(get_trimestre_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return trimestre_service.get_all_trimestre()
