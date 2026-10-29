from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.enumeration import FiltreInscription
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.eleve.eleve_repository import EleveRepository
from schemas.eleve.eleve_dto import (
    EleveRechercheResponseDTO,
    EleveResponseDTO,
    EleveUpdateDTO,
    PaginatedEleveClasse,
)
from services.eleve.eleve_service import EleveService

router = APIRouter()


def get_eleve_service(db: Session = Depends(get_db)):
    eleve_repo = EleveRepository(db)
    annee_repo = AnneeRepository(db)
    classe_repo = ClasseRepository(db)
    return EleveService(eleve_repo, annee_repo, classe_repo)


@router.patch(
    "/update/{eleve_id}",
    summary="Modifier les informations d'un eleve",
    status_code=200,
    response_model=EleveResponseDTO,
)
def update_eleve(
    eleve_id: int,
    eleve_update: EleveUpdateDTO,
    eleve_service: Annotated[EleveService, Depends(get_eleve_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.MODIFIER))],
):
    return eleve_service.update_eleve(eleve_update, eleve_id)


@router.get(
    "/one/{eleve_id}",
    summary="Recuperer un eleve",
    status_code=200,
    response_model=EleveResponseDTO,
)
def get_one_eleve(
    eleve_id: int,
    eleve_service: Annotated[EleveService, Depends(get_eleve_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.CONSULTER))],
):
    return eleve_service.get_one_eleve(eleve_id)


@router.get(
    "/all",
    summary="Recuperer tous les eleves",
    status_code=200,
    response_model=list[EleveResponseDTO],
)
def get_all_eleve(
    eleve_service: Annotated[EleveService, Depends(get_eleve_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.CONSULTER))],
):
    return eleve_service.get_all_eleve()


@router.get(
    "/search",
    summary="Rechercher des eleves dans toute l'ecole (nom, prenom ou matricule)",
    status_code=200,
    response_model=list[EleveRechercheResponseDTO],
)
def search_eleves(
    eleve_service: Annotated[EleveService, Depends(get_eleve_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.RECHERCHER))],
    q: Annotated[str, Query(min_length=3, max_length=100, description="Nom, prenom ou matricule (3 caracteres minimum)")] = ...,
    limit: Annotated[int, Query(ge=1, le=50, description="Nombre maximum de resultats")] = 20,
):
    return eleve_service.search_eleves(q, limit)


@router.get(
    "/by-classe/{id_classe}",
    summary="Recuperer les eleves d'une classe pour l'annee en cours (pagines ; sans page ni page_size : toute la liste, pour l'export)",
    status_code=200,
    response_model=PaginatedEleveClasse,
)
def get_eleves_by_classe(
    id_classe: int,
    eleve_service: Annotated[EleveService, Depends(get_eleve_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.CONSULTER))],
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'elements par page")] = None,
    q: Annotated[str | None, Query(max_length=100, description="Filtre sur le nom, le prenom ou le matricule")] = None,
    genre: Annotated[str | None, Query(pattern="^[MF]$", description="Filtre sur le genre (M ou F)")] = None,
    statut: Annotated[FiltreInscription, Query(description="tous, inscrit (inscription finalisee) ou non_inscrit")] = FiltreInscription.TOUS,
):
    return eleve_service.get_eleves_by_classe(id_classe, page, page_size, q, genre, statut)
