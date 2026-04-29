from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.serie_repository import SerieRepository
from schemas.administration.serie_dto import SerieCreateDTO, SerieResponseDTO, SerieUpdateDTO
from services.administration.serie_service import SerieService

router = APIRouter()


def get_serie_service(db: Session = Depends(get_db)):
    serie_repo = SerieRepository(db)
    annee_repo = AnneeRepository(db)
    return SerieService(serie_repo, annee_repo)


@router.post(
    "/add",
    summary="Ajouter une serie",
    status_code=201,
    response_model=SerieResponseDTO,
)
def add_serie(
    serie_in: SerieCreateDTO,
    serie_service: Annotated[SerieService, Depends(get_serie_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return serie_service.add_serie(serie_in)


@router.patch(
    "/update/{serie_id}",
    summary="Modifier une serie",
    status_code=200,
    response_model=SerieResponseDTO,
)
def update_serie(
    serie_id: int,
    serie_update: SerieUpdateDTO,
    serie_service: Annotated[SerieService, Depends(get_serie_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return serie_service.update_serie(serie_update, serie_id)


@router.delete(
    "/delete/{serie_id}",
    summary="Supprimer une serie",
    status_code=200,
)
def delete_serie(
    serie_id: int,
    serie_service: Annotated[SerieService, Depends(get_serie_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return serie_service.delete_serie(serie_id)


@router.get(
    "/{serie_id}",
    summary="Recuperer une serie",
    status_code=200,
    response_model=SerieResponseDTO,
)
def get_one_serie(
    serie_id: int,
    serie_service: Annotated[SerieService, Depends(get_serie_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return serie_service.get_one_serie(serie_id)


@router.get(
    "/all",
    summary="Recuperer toutes les series",
    status_code=200,
    response_model=list[SerieResponseDTO],
)
def get_all_serie(
    serie_service: Annotated[SerieService, Depends(get_serie_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return serie_service.get_all_serie()
