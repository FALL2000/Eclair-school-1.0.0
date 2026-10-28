from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission, require_super_admin
from common.permissions import Action, Module
from common.enumeration import StatutPaiementTranche
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.scolarite.reglement_repository import ReglementRepository
from repositories.scolarite.tranche_pension_repository import TranchePensionRepository
from schemas.scolarite.reglement_dto import (
    PaginatedHistoriqueReglement,
    PaginatedReglement,
    ReglementCreateDTO,
    ReglementRecuDTO,
    ReglementEleveTrancheResponseDTO,
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
    tranche_pension_repo = TranchePensionRepository(db)
    return ReglementService(reglement_repo, annee_repo, classe_repo, tranche_pension_repo)


@router.post(
    "/add",
    summary="Enregistrer un règlement",
    status_code=201,
    response_model=ReglementResponseDTO,
)
def add_reglement(
    reglement_in: ReglementCreateDTO,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.AJOUTER))],
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
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.MODIFIER))],
):
    return reglement_service.update_reglement(reglement_id, reglement_update)


@router.patch(
    "/annuler/{reglement_id}",
    summary="Annuler un règlement",
    status_code=200,
    response_model=ReglementResponseDTO,
)
def annuler_reglement(
    reglement_id: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.ANNULER))],
):
    return reglement_service.annuler_reglement(reglement_id)


@router.delete(
    "/delete/{reglement_id}",
    summary="Supprimer un règlement",
    status_code=200,
)
def delete_reglement(
    reglement_id: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_super_admin)],
):
    return reglement_service.delete_reglement(reglement_id)


@router.get(
    "/recu/{reglement_id}",
    summary="Données du reçu d'un règlement (impression ou duplicata) : situation de la tranche au moment du règlement",
    status_code=200,
    response_model=ReglementRecuDTO,
)
def get_recu_reglement(
    reglement_id: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.CONSULTER))],
):
    return reglement_service.get_recu(reglement_id)


@router.get(
    "/historique",
    summary="Historique des règlements de l'année en cours (plus récents en premier, paginé, filtres par dates et par élève)",
    status_code=200,
    response_model=PaginatedHistoriqueReglement,
)
def get_historique_reglements(
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.CONSULTER))],
    date_debut: Annotated[date | None, Query(description="Date de règlement minimale (incluse)")] = None,
    date_fin: Annotated[date | None, Query(description="Date de règlement maximale (incluse)")] = None,
    q: Annotated[str | None, Query(max_length=100, description="Nom, prénom ou matricule de l'élève")] = None,
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'éléments par page")] = None,
):
    return reglement_service.get_historique(date_debut, date_fin, q, page, page_size)


@router.get(
    "/all",
    summary="Récupérer tous les règlements paginés (ordre décroissant par date)",
    status_code=200,
    response_model=PaginatedReglement,
)
def get_all_reglements(
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.CONSULTER))],
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
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.CONSULTER))],
):
    return reglement_service.get_reglements_by_classe(id_classe)


@router.get(
    "/by-classe/{id_classe}/tranche/{id_tranche_pension}",
    summary="Récupérer la situation de paiement d'une tranche de pension des élèves d'une classe pour l'année en cours",
    status_code=200,
    response_model=list[ReglementEleveTrancheResponseDTO],
)
def get_reglements_by_classe_tranche(
    id_classe: int,
    id_tranche_pension: int,
    reglement_service: Annotated[ReglementService, Depends(get_reglement_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.REGLEMENT, Action.CONSULTER))],
    statut_paiement: Annotated[StatutPaiementTranche | None, Query(
        description="Filtrer les élèves : total (tranche totalement réglée), partiel (partiellement réglée), aucun (rien réglé)")] = None,
):
    return reglement_service.get_reglements_by_classe_tranche(id_classe, id_tranche_pension, statut_paiement)
