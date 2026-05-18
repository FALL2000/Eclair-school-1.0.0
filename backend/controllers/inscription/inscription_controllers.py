from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from repositories.administration.classe_repository import ClasseRepository
from common.dependencies import check_permission_user, get_db
from repositories.eleve.eleve_repository import EleveRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.inscription.inscription_dto import (
    InscriptionNouveauEleveRequestDTO,
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
    current_user: Annotated[dict[str, Any], Depends(check_permission_user)],
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
    current_user: Annotated[dict[str, Any], Depends(check_permission_user)]
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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    page: Annotated[int | None, Query(
        description="page actuelle de la pagination")] = None,
    page_size: Annotated[int | None, Query(
        description="Nombre elements sur une page de pagination")] = None
):
    return inscription_service.get_inscriptions_by_classe(id_classe, page, page_size)
