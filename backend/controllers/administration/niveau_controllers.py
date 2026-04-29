from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.niveau_repository import NiveauRepository
from schemas.administration.niveau_dto import NiveauCreateDTO, NiveauResponseDTO, NiveauUpdateDTO
from services.administration.niveau_service import NiveauService

router = APIRouter()


def get_niveau_service(db: Session = Depends(get_db)):
    niveau_repo = NiveauRepository(db)
    annee_repo = AnneeRepository(db)
    return NiveauService(niveau_repo, annee_repo)


@router.post(
    "/add/{cycle_id}/{serie_id}",
    summary="Ajouter un niveau",
    status_code=201,
    response_model=NiveauResponseDTO,
)
def add_niveau(
    cycle_id: int,
    serie_id: int,
    niveau_in: NiveauCreateDTO,
    niveau_service: Annotated[NiveauService, Depends(get_niveau_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return niveau_service.add_niveau(niveau_in, cycle_id, serie_id)


@router.patch(
    "/update/{niveau_id}",
    summary="Modifier un niveau",
    status_code=200,
    response_model=NiveauResponseDTO,
)
def update_niveau(
    niveau_id: int,
    niveau_update: NiveauUpdateDTO,
    niveau_service: Annotated[NiveauService, Depends(get_niveau_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return niveau_service.update_niveau(niveau_update, niveau_id)


@router.delete(
    "/delete/{niveau_id}",
    summary="Supprimer un niveau",
    status_code=200,
)
def delete_niveau(
    niveau_id: int,
    niveau_service: Annotated[NiveauService, Depends(get_niveau_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return niveau_service.delete_niveau(niveau_id)


@router.get(
    "/{niveau_id}",
    summary="Recuperer un niveau",
    status_code=200,
    response_model=NiveauResponseDTO,
)
def get_one_niveau(
    niveau_id: int,
    niveau_service: Annotated[NiveauService, Depends(get_niveau_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return niveau_service.get_one_niveau(niveau_id)


@router.get(
    "/all",
    summary="Recuperer tous les niveaux",
    status_code=200,
    response_model=list[NiveauResponseDTO],
)
def get_all_niveau(
    niveau_service: Annotated[NiveauService, Depends(get_niveau_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return niveau_service.get_all_niveau()
