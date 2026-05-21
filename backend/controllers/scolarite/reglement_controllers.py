from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.scolarite.reglement_repository import ReglementRepository
from schemas.scolarite.reglement_dto import (
    PaginatedReglement,
    ReglementCreateDTO,
    ReglementParClasseResponseDTO,
    ReglementResponseDTO,
    ReglementUpdateDTO,
)
from services.scolarite.reglement_service import ReglementService

router = APIRouter()


def get_reglement_service(db: Session = Depends(get_db)):
    reglement_repo = ReglementRepository(db)
    annee_repo = AnneeRepository(db)
    classe_repo = ClasseRepository(db)
    return ReglementService(reglement_repo, annee_repo, classe_repo)


@router.post(
    "/add",
    summary="Enregistrer un règlement",
    status_code=201,
    response_model=ReglementResponseDTO,
)
def add_reglement(
    reglement_in: ReglementCreateDTO,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    current_user: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_eleve: Annotated[int, Query(description="Id de l'élève")] = ...,
    id_tranche_pension: Annotated[int, Query(description="Id de la tranche de pension")] = ...,
):
    return reglement_service.add_reglement(reglement_in, id_eleve, id_tranche_pension, current_user["user"])


@router.patch(
    "/update/{reglement_id}",
    summary="Modifier un règlement",
    status_code=200,
    response_model=ReglementResponseDTO,
)
def update_reglement(
    reglement_id: int,
    reglement_update: ReglementUpdateDTO,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return reglement_service.update_reglement(reglement_id, reglement_update)


@router.delete(
    "/delete/{reglement_id}",
    summary="Supprimer un règlement",
    status_code=200,
)
def delete_reglement(
    reglement_id: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return reglement_service.delete_reglement(reglement_id)


@router.get(
    "/all",
    summary="Récupérer tous les règlements paginés (ordre décroissant par date)",
    status_code=200,
    response_model=PaginatedReglement,
)
def get_all_reglements(
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    page: Annotated[int | None, Query(description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(description="Nombre d'éléments par page")] = None,
):
    return reglement_service.get_all_reglements(page, page_size)


@router.get(
    "/by-classe/{id_classe}",
    summary="Récupérer les règlements des élèves d'une classe pour l'année en cours",
    status_code=200,
    response_model=list[ReglementParClasseResponseDTO],
)
def get_reglements_by_classe(
    id_classe: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return reglement_service.get_reglements_by_classe(id_classe)
