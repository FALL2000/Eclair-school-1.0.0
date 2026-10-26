from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from repositories.administration.classe_repository import ClasseRepository
from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.eleve.eleve_repository import EleveRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.inscription.inscription_dto import (
    InscriptionHistoriqueDTO,
    InscriptionModificationDTO,
    InscriptionNouveauEleveRequestDTO,
    PaginatedHistoriqueInscription,
    InscriptionResponseDTO,
    PaginatedInscription,
)
from services.inscription.inscription_service import InscriptionService

router = APIRouter()


def get_inscription_service(db: Session = Depends(get_db)):
    eleve_repo = EleveRepository(db)
    inscription_repo = InscriptionRepository(db)
    classe_repo = ClasseRepository(db)
    return InscriptionService(eleve_repo, inscription_repo, classe_repo)


@router.post(
    "/nouveau-eleve",
    summary="Inscrire un nouvel eleve (eleve + inscription)",
    status_code=201,
    response_model=InscriptionResponseDTO,
)
def inscrire_nouveau_eleve(
    body: InscriptionNouveauEleveRequestDTO,
    inscription_service: Annotated[InscriptionService, Depends(get_inscription_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.INSCRIRE))],
):
    return inscription_service.inscrire_nouveau_eleve(body, current_user["user"])


@router.post(
    "/ancien-eleve/{inscription_id}",
    summary="Finaliser l'inscription d'un ancien eleve",
    status_code=200,
    response_model=InscriptionResponseDTO,
)
def finaliser_inscription_ancien_eleve(
    inscription_id: int,
    inscription_service: Annotated[InscriptionService, Depends(get_inscription_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.INSCRIRE))]
):
    return inscription_service.finaliser_inscription_ancien_eleve(inscription_id, current_user["user"])


@router.get(
    "/by_classe/{id_classe}",
    summary="Finaliser l'inscription d'un ancien eleve",
    status_code=200,
    response_model=PaginatedInscription,
)
def get_inscriptions_by_classe(
    id_classe: int,
    inscription_service: Annotated[InscriptionService, Depends(get_inscription_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.CONSULTER))],
    page: Annotated[int | None, Query(
        description="page actuelle de la pagination")] = None,
    page_size: Annotated[int | None, Query(
        description="Nombre elements sur une page de pagination")] = None
):
    return inscription_service.get_inscriptions_by_classe(id_classe, page, page_size)


@router.get(
    "/historique",
    summary="Historique des inscriptions (plus recentes en premier, pagine, filtres par dates et par eleve)",
    status_code=200,
    response_model=PaginatedHistoriqueInscription,
)
def get_historique_inscriptions(
    inscription_service: Annotated[InscriptionService, Depends(get_inscription_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.CONSULTER))],
    date_debut: Annotated[date | None, Query(description="Date d'inscription minimale (incluse)")] = None,
    date_fin: Annotated[date | None, Query(description="Date d'inscription maximale (incluse)")] = None,
    q: Annotated[str | None, Query(max_length=100, description="Nom, prenom ou matricule de l'eleve")] = None,
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'elements par page")] = None,
):
    return inscription_service.get_historique(date_debut, date_fin, q, page, page_size)


@router.patch(
    "/update/{inscription_id}",
    summary="Modifier la classe ou le statut redoublant d'une inscription de l'annee en cours",
    status_code=200,
    response_model=InscriptionHistoriqueDTO,
)
def update_inscription(
    inscription_id: int,
    data: InscriptionModificationDTO,
    inscription_service: Annotated[InscriptionService, Depends(get_inscription_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.INSCRIRE))],
):
    return inscription_service.update_inscription(inscription_id, data, current_user["user"])
