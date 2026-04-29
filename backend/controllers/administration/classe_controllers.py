from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from schemas.administration.classe_dto import ClasseCreateDTO, ClasseResponseDTO, ClasseUpdateDTO
from services.administration.classe_service import ClasseService

router = APIRouter()


def get_classe_service(db: Session = Depends(get_db)):
    classe_repo = ClasseRepository(db)
    annee_repo = AnneeRepository(db)
    return ClasseService(classe_repo, annee_repo)


@router.post(
    "/add/{niveau_id}",
    summary="Ajouter une classe",
    status_code=201,
    response_model=ClasseResponseDTO,
)
def add_classe(
    niveau_id: int,
    classe_in: ClasseCreateDTO,
    classe_service: Annotated[ClasseService, Depends(get_classe_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return classe_service.add_classe(classe_in, niveau_id)


@router.patch(
    "/update/{classe_id}",
    summary="Modifier une classe",
    status_code=200,
    response_model=ClasseResponseDTO,
)
def update_classe(
    classe_id: int,
    classe_update: ClasseUpdateDTO,
    classe_service: Annotated[ClasseService, Depends(get_classe_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return classe_service.update_classe(classe_update, classe_id)


@router.delete(
    "/delete/{classe_id}",
    summary="Supprimer une classe",
    status_code=200,
)
def delete_classe(
    classe_id: int,
    classe_service: Annotated[ClasseService, Depends(get_classe_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return classe_service.delete_classe(classe_id)


@router.get(
    "/{classe_id}",
    summary="Recuperer une classe",
    status_code=200,
    response_model=ClasseResponseDTO,
)
def get_one_classe(
    classe_id: int,
    classe_service: Annotated[ClasseService, Depends(get_classe_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return classe_service.get_one_classe(classe_id)


@router.get(
    "/all",
    summary="Recuperer toutes les classes",
    status_code=200,
    response_model=list[ClasseResponseDTO],
)
def get_all_classe(
    classe_service: Annotated[ClasseService, Depends(get_classe_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return classe_service.get_all_classe()
