from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_repository import GroupeMatiereRepository
from schemas.administration.groupe_matiere_dto import (
    GroupeMatiereCreateDTO,
    GroupeMatiereResponseDTO,
    GroupeMatiereUpdateDTO,
)
from services.administration.groupe_matiere_service import GroupeMatiereService

router = APIRouter()


def get_groupe_matiere_service(db: Session = Depends(get_db)):
    groupe_matiere_repo = GroupeMatiereRepository(db)
    annee_repo = AnneeRepository(db)
    return GroupeMatiereService(groupe_matiere_repo, annee_repo)


@router.post(
    "/add",
    summary="Ajouter un groupe de matiere",
    status_code=201,
    response_model=GroupeMatiereResponseDTO,
)
def add_groupe_matiere(
    groupe_matiere_in: GroupeMatiereCreateDTO,
    groupe_matiere_service: Annotated[GroupeMatiereService, Depends(get_groupe_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_service.add_groupe_matiere(groupe_matiere_in)


@router.patch(
    "/update/{groupe_matiere_id}",
    summary="Modifier un groupe de matiere",
    status_code=200,
    response_model=GroupeMatiereResponseDTO,
)
def update_groupe_matiere(
    groupe_matiere_id: int,
    groupe_matiere_update: GroupeMatiereUpdateDTO,
    groupe_matiere_service: Annotated[GroupeMatiereService, Depends(get_groupe_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_service.update_groupe_matiere(groupe_matiere_update, groupe_matiere_id)


@router.delete(
    "/delete/{groupe_matiere_id}",
    summary="Supprimer un groupe de matiere",
    status_code=200,
)
def delete_groupe_matiere(
    groupe_matiere_id: int,
    groupe_matiere_service: Annotated[GroupeMatiereService, Depends(get_groupe_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_service.delete_groupe_matiere(groupe_matiere_id)


@router.get(
    "/{groupe_matiere_id}",
    summary="Recuperer un groupe de matiere",
    status_code=200,
    response_model=GroupeMatiereResponseDTO,
)
def get_one_groupe_matiere(
    groupe_matiere_id: int,
    groupe_matiere_service: Annotated[GroupeMatiereService, Depends(get_groupe_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_service.get_one_groupe_matiere(groupe_matiere_id)


@router.get(
    "/all",
    summary="Recuperer tous les groupes de matieres",
    status_code=200,
    response_model=list[GroupeMatiereResponseDTO],
)
def get_all_groupe_matiere(
    groupe_matiere_service: Annotated[GroupeMatiereService, Depends(get_groupe_matiere_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_service.get_all_groupe_matiere()
