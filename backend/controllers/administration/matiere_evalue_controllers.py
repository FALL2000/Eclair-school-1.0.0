from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from schemas.administration.matiere_evalue_dto import (
    MatiereEvalueCreateDTO,
    MatiereEvalueResponseDTO,
    MatiereEvalueUpdateDTO,
)
from services.administration.matiere_evalue_service import MatiereEvalueService

router = APIRouter()


def get_matiere_evalue_service(db: Session = Depends(get_db)):
    matiere_evalue_repo = MatiereEvalueRepository(db)
    groupe_matiere_evalue_repo = GroupeMatiereEvalueRepository(db)
    annee_repo = AnneeRepository(db)
    return MatiereEvalueService(matiere_evalue_repo, groupe_matiere_evalue_repo, annee_repo)


@router.post(
    "/add/{groupe_matiere_evalue_id}",
    summary="Ajouter une matiere evaluee",
    status_code=201,
    response_model=MatiereEvalueResponseDTO,
)
def add_matiere_evalue(
    groupe_matiere_evalue_id: int,
    matiere_evalue_in: MatiereEvalueCreateDTO,
    matiere_evalue_service: Annotated[MatiereEvalueService, Depends(get_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_evalue_service.add_matiere_evalue(matiere_evalue_in, groupe_matiere_evalue_id)


@router.patch(
    "/update/{matiere_evalue_id}",
    summary="Modifier une matiere evaluee",
    status_code=200,
    response_model=MatiereEvalueResponseDTO,
)
def update_matiere_evalue(
    matiere_evalue_id: int,
    matiere_evalue_update: MatiereEvalueUpdateDTO,
    matiere_evalue_service: Annotated[MatiereEvalueService, Depends(get_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_evalue_service.update_matiere_evalue(matiere_evalue_update, matiere_evalue_id)


@router.delete(
    "/delete/{matiere_evalue_id}",
    summary="Supprimer une matiere evaluee",
    status_code=200,
)
def delete_matiere_evalue(
    matiere_evalue_id: int,
    matiere_evalue_service: Annotated[MatiereEvalueService, Depends(get_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_evalue_service.delete_matiere_evalue(matiere_evalue_id)


@router.get(
    "/{matiere_evalue_id}",
    summary="Recuperer une matiere evaluee",
    status_code=200,
    response_model=MatiereEvalueResponseDTO,
)
def get_one_matiere_evalue(
    matiere_evalue_id: int,
    matiere_evalue_service: Annotated[MatiereEvalueService, Depends(get_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_evalue_service.get_one_matiere_evalue(matiere_evalue_id)


@router.get(
    "/all",
    summary="Recuperer toutes les matieres evaluees",
    status_code=200,
    response_model=list[MatiereEvalueResponseDTO],
)
def get_all_matiere_evalue(
    matiere_evalue_service: Annotated[MatiereEvalueService, Depends(get_matiere_evalue_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return matiere_evalue_service.get_all_matiere_evalue()
