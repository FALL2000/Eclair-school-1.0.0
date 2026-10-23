from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.bareme_repository import BaremeRepository
from schemas.administration.bareme_dto import (
    BaremeCreateDTO,
    BaremeResponseDTO,
    BaremeUpdateDTO,
)
from services.administration.bareme_service import BaremeService

router = APIRouter()


def get_bareme_service(db: Session = Depends(get_db)):
    bareme_repo = BaremeRepository(db)
    return BaremeService(bareme_repo)


@router.post(
    "/add",
    summary="Ajouter un barème de notation",
    status_code=201,
    response_model=BaremeResponseDTO,
)
def add_bareme(
    bareme_in: BaremeCreateDTO,
    bareme_service: Annotated[BaremeService, Depends(get_bareme_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BAREME, Action.AJOUTER))],
):
    return bareme_service.add_bareme(bareme_in)


@router.patch(
    "/update/{bareme_id}",
    summary="Modifier un barème de notation",
    status_code=200,
    response_model=BaremeResponseDTO,
)
def update_bareme(
    bareme_id: int,
    bareme_update: BaremeUpdateDTO,
    bareme_service: Annotated[BaremeService, Depends(get_bareme_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BAREME, Action.MODIFIER))],
):
    return bareme_service.update_bareme(bareme_update, bareme_id)


@router.delete(
    "/delete/{bareme_id}",
    summary="Supprimer un barème de notation",
    status_code=200,
)
def delete_bareme(
    bareme_id: int,
    bareme_service: Annotated[BaremeService, Depends(get_bareme_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BAREME, Action.SUPPRIMER))],
):
    return bareme_service.delete_bareme(bareme_id)


@router.get(
    "/one/{bareme_id}",
    summary="Recuperer un barème de notation",
    status_code=200,
    response_model=BaremeResponseDTO,
)
def get_one_bareme(
    bareme_id: int,
    bareme_service: Annotated[BaremeService, Depends(get_bareme_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BAREME, Action.CONSULTER))],
):
    return bareme_service.get_one_bareme(bareme_id)


@router.get(
    "/all",
    summary="Recuperer tous les barèmes de notation",
    status_code=200,
    response_model=list[BaremeResponseDTO],
)
def get_all_baremes(
    bareme_service: Annotated[BaremeService, Depends(get_bareme_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BAREME, Action.CONSULTER))],
):
    return bareme_service.get_all_baremes()
