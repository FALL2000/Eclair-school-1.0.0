from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.appreciation_repository import AppreciationRepository
from schemas.administration.appreciation_dto import (
    AppreciationCreateDTO,
    AppreciationResponseDTO,
    AppreciationUpdateDTO,
)
from services.administration.appreciation_service import AppreciationService

router = APIRouter()


def get_appreciation_service(db: Session = Depends(get_db)):
    appreciation_repo = AppreciationRepository(db)
    return AppreciationService(appreciation_repo)


@router.post(
    "/add",
    summary="Ajouter une appreciation",
    status_code=201,
    response_model=AppreciationResponseDTO,
)
def add_appreciation(
    appreciation_in: AppreciationCreateDTO,
    appreciation_service: Annotated[AppreciationService, Depends(get_appreciation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return appreciation_service.add_appreciation(appreciation_in)


@router.patch(
    "/update/{appreciation_id}",
    summary="Modifier une appreciation",
    status_code=200,
    response_model=AppreciationResponseDTO,
)
def update_appreciation(
    appreciation_id: int,
    appreciation_update: AppreciationUpdateDTO,
    appreciation_service: Annotated[AppreciationService, Depends(get_appreciation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return appreciation_service.update_appreciation(appreciation_update, appreciation_id)


@router.delete(
    "/delete/{appreciation_id}",
    summary="Supprimer une appreciation",
    status_code=200,
)
def delete_appreciation(
    appreciation_id: int,
    appreciation_service: Annotated[AppreciationService, Depends(get_appreciation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return appreciation_service.delete_appreciation(appreciation_id)


@router.get(
    "/{appreciation_id}",
    summary="Recuperer une appreciation",
    status_code=200,
    response_model=AppreciationResponseDTO,
)
def get_one_appreciation(
    appreciation_id: int,
    appreciation_service: Annotated[AppreciationService, Depends(get_appreciation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return appreciation_service.get_one_appreciation(appreciation_id)


@router.get(
    "/all",
    summary="Recuperer toutes les appreciations",
    status_code=200,
    response_model=list[AppreciationResponseDTO],
)
def get_all_appreciation(
    appreciation_service: Annotated[AppreciationService, Depends(get_appreciation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return appreciation_service.get_all_appreciation()
