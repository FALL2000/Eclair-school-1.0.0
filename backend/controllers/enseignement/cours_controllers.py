from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignement.cours_repository import CoursRepository
from schemas.enseignement.cours_dto import (
    CoursBulkCreateDTO,
    CoursBulkUpdateDTO,
    CoursCreateDTO,
    CoursParClasseResponseDTO,
    CoursParEnseignantResponseDTO,
    CoursResponseDTO,
    CoursUpdateDTO,
)
from services.enseignement.cours_service import CoursService

router = APIRouter()


def get_cours_service(db: Session = Depends(get_db)):
    cours_repo = CoursRepository(db)
    annee_repo = AnneeRepository(db)
    return CoursService(cours_repo, annee_repo)


@router.get(
    "/by-enseignant",
    summary="Récupérer les cours d'un enseignant pour l'année en cours",
    status_code=200,
    response_model=list[CoursParEnseignantResponseDTO],
)
def get_cours_by_enseignant(
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_enseignant: Annotated[int, Query(description="Id de l'enseignant")] = ...,
):
    return cours_service.get_cours_by_enseignant(id_enseignant)


@router.get(
    "/by-classe",
    summary="Récupérer les cours d'une classe pour l'année en cours",
    status_code=200,
    response_model=list[CoursParClasseResponseDTO],
)
def get_cours_by_classe(
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    jour: Annotated[Optional[str], Query(description="Jour du cours (Lundi, Mardi, ...)")] = None,
):
    return cours_service.get_cours_by_classe(id_classe, jour)


@router.post(
    "/add",
    summary="Ajouter un cours",
    status_code=201,
    response_model=CoursResponseDTO,
)
def add_cours(
    data: CoursCreateDTO,
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_enseignant: Annotated[int, Query(description="Id de l'enseignant")] = ...,
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_matiere: Annotated[int, Query(description="Id de la matière")] = ...,
):
    return cours_service.add_cours(data, id_enseignant, id_classe, id_matiere)


@router.post(
    "/add-bulk",
    summary="Ajouter des cours en masse",
    status_code=201,
    response_model=list[CoursResponseDTO],
)
def add_bulk_cours(
    data: CoursBulkCreateDTO,
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cours_service.add_bulk_cours(data)


@router.patch(
    "/update/{cours_id}",
    summary="Modifier un cours",
    status_code=200,
    response_model=CoursResponseDTO,
)
def update_cours(
    cours_id: int,
    data: CoursUpdateDTO,
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cours_service.update_cours(cours_id, data)


@router.patch(
    "/update-bulk",
    summary="Modifier plusieurs cours en masse",
    status_code=200,
    response_model=list[CoursResponseDTO],
)
def update_bulk_cours(
    data: CoursBulkUpdateDTO,
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cours_service.update_bulk_cours(data)


@router.delete(
    "/delete/{cours_id}",
    summary="Supprimer un cours",
    status_code=200,
)
def delete_cours(
    cours_id: int,
    cours_service: Annotated[CoursService, Depends(get_cours_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return cours_service.delete_cours(cours_id)
