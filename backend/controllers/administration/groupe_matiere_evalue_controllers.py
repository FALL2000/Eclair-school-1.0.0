from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.niveau_repository import NiveauRepository
from schemas.administration.groupe_matiere_evalues_dto import (
    GroupeMatiereEvalueCreateDTO,
    GroupeMatiereEvalueResponseDTO,
    GroupeMatiereEvalueUpdateDTO,
)
from services.administration.groupe_matiere_evalue_service import GroupeMatiereEvalueService

router = APIRouter()


def get_groupe_matiere_evalue_service(db: Session = Depends(get_db)):
    groupe_matiere_evalue_repo = GroupeMatiereEvalueRepository(db)
    niveau_repo = NiveauRepository(db)
    annee_repo = AnneeRepository(db)
    return GroupeMatiereEvalueService(groupe_matiere_evalue_repo, niveau_repo, annee_repo)


@router.post(
    "/add/{niveau_id}",
    summary="Ajouter un groupe de matiere evalue",
    status_code=201,
    response_model=GroupeMatiereEvalueResponseDTO,
)
def add_groupe_matiere_evalue(
    niveau_id: int,
    groupe_matiere_evalue_in: GroupeMatiereEvalueCreateDTO,
    groupe_matiere_evalue_service: Annotated[GroupeMatiereEvalueService, Depends(get_groupe_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_evalue_service.add_groupe_matiere_evalue(groupe_matiere_evalue_in, niveau_id)


@router.patch(
    "/update/{groupe_matiere_evalue_id}",
    summary="Modifier un groupe de matiere evalue",
    status_code=200,
    response_model=GroupeMatiereEvalueResponseDTO,
)
def update_groupe_matiere_evalue(
    groupe_matiere_evalue_id: int,
    groupe_matiere_evalue_update: GroupeMatiereEvalueUpdateDTO,
    groupe_matiere_evalue_service: Annotated[GroupeMatiereEvalueService, Depends(get_groupe_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_evalue_service.update_groupe_matiere_evalue(
        groupe_matiere_evalue_update, groupe_matiere_evalue_id
    )


@router.delete(
    "/delete/{groupe_matiere_evalue_id}",
    summary="Supprimer un groupe de matiere evalue",
    status_code=200,
)
def delete_groupe_matiere_evalue(
    groupe_matiere_evalue_id: int,
    groupe_matiere_evalue_service: Annotated[GroupeMatiereEvalueService, Depends(get_groupe_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_evalue_service.delete_groupe_matiere_evalue(groupe_matiere_evalue_id)


@router.get(
    "/{groupe_matiere_evalue_id}",
    summary="Recuperer un groupe de matiere evalue",
    status_code=200,
    response_model=GroupeMatiereEvalueResponseDTO,
)
def get_one_groupe_matiere_evalue(
    groupe_matiere_evalue_id: int,
    groupe_matiere_evalue_service: Annotated[GroupeMatiereEvalueService, Depends(get_groupe_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_evalue_service.get_one_groupe_matiere_evalue(groupe_matiere_evalue_id)


@router.get(
    "/all",
    summary="Recuperer tous les groupes de matieres evalues",
    status_code=200,
    response_model=list[GroupeMatiereEvalueResponseDTO],
)
def get_all_groupe_matiere_evalue(
    groupe_matiere_evalue_service: Annotated[GroupeMatiereEvalueService, Depends(get_groupe_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return groupe_matiere_evalue_service.get_all_groupe_matiere_evalue()
