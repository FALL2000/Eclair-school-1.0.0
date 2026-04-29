from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_repository import GroupeMatiereRepository
from repositories.administration.matiere_repository import MatiereRepository
from schemas.administration.matiere_dto import MatiereCreateDTO, MatiereResponseDTO, MatiereUpdateDTO
from services.administration.matiere_service import MatiereService

router = APIRouter()


def get_matiere_service(db: Session = Depends(get_db)):
    matiere_repo = MatiereRepository(db)
    groupe_matiere_repo = GroupeMatiereRepository(db)
    annee_repo = AnneeRepository(db)
    return MatiereService(matiere_repo, groupe_matiere_repo, annee_repo)


@router.post(
    "/add/{groupe_matiere_id}",
    summary="Ajouter une matiere",
    status_code=201,
    response_model=MatiereResponseDTO,
)
def add_matiere(
    groupe_matiere_id: int,
    matiere_in: MatiereCreateDTO,
    matiere_service: Annotated[MatiereService, Depends(get_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_service.add_matiere(matiere_in, groupe_matiere_id)


@router.patch(
    "/update/{matiere_id}",
    summary="Modifier une matiere",
    status_code=200,
    response_model=MatiereResponseDTO,
)
def update_matiere(
    matiere_id: int,
    matiere_update: MatiereUpdateDTO,
    matiere_service: Annotated[MatiereService, Depends(get_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_service.update_matiere(matiere_update, matiere_id)


@router.delete(
    "/delete/{matiere_id}",
    summary="Supprimer une matiere",
    status_code=200,
)
def delete_matiere(
    matiere_id: int,
    matiere_service: Annotated[MatiereService, Depends(get_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_service.delete_matiere(matiere_id)


@router.get(
    "/{matiere_id}",
    summary="Recuperer une matiere",
    status_code=200,
    response_model=MatiereResponseDTO,
)
def get_one_matiere(
    matiere_id: int,
    matiere_service: Annotated[MatiereService, Depends(get_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_service.get_one_matiere(matiere_id)


@router.get(
    "/all",
    summary="Recuperer toutes les matieres",
    status_code=200,
    response_model=list[MatiereResponseDTO],
)
def get_all_matiere(
    matiere_service: Annotated[MatiereService, Depends(get_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_service.get_all_matiere()
