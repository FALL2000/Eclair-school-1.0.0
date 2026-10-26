from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.enumeration import StatutPaiementTranche
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.enseignants.enseignant_repository import EnseignantRepository
from repositories.enseignants.versement_salaire_repository import VersementSalaireRepository
from schemas.enseignants.salaire_dto import (
    PaginatedSalaireMois,
    MoyenPaiementEnseignantDTO,
    MoyenPaiementUpdateDTO,
    PaginatedMoyenPaiement,
    PaginatedVersementSalaire,
    SalaireEnseignantDetailDTO,
    VersementSalaireCreateDTO,
    VersementSalaireResponseDTO,
)
from services.enseignants.salaire_service import SalaireService, peut_voir_numero_compte

router = APIRouter()


def get_salaire_service(db: Session = Depends(get_db)):
    return SalaireService(
        VersementSalaireRepository(db),
        EnseignantRepository(db),
        AnneeRepository(db),
        ConfigurationRepository(db),
    )


@router.get(
    "/mois",
    summary="Salaires des enseignants pour un mois de l'annee scolaire (du, verse, reste), pagines",
    status_code=200,
    response_model=PaginatedSalaireMois,
)
def get_salaires_mois(
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.CONSULTER))],
    mois: Annotated[int, Query(ge=1, le=12, description="Mois (1 a 12)")] = ...,
    annee_civile: Annotated[int, Query(description="Annee civile du mois (ex : 2026)")] = ...,
    q: Annotated[str | None, Query(max_length=100, description="Nom ou prenom de l'enseignant")] = None,
    statut: Annotated[StatutPaiementTranche | None, Query(description="total, partiel ou aucun")] = None,
    id_matiere: Annotated[int | None, Query(description="Id de la matiere enseignee")] = None,
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'elements par page")] = None,
):
    return salaire_service.get_salaires_mois(mois, annee_civile, q, statut, page, page_size, id_matiere)


@router.get(
    "/enseignant/{id_enseignant}",
    summary="Salaire d'un enseignant pour un mois, avec ses versements",
    status_code=200,
    response_model=SalaireEnseignantDetailDTO,
)
def get_salaire_enseignant(
    id_enseignant: int,
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.CONSULTER))],
    mois: Annotated[int, Query(ge=1, le=12, description="Mois (1 a 12)")] = ...,
    annee_civile: Annotated[int, Query(description="Annee civile du mois (ex : 2026)")] = ...,
):
    return salaire_service.get_salaire_enseignant(id_enseignant, mois, annee_civile, peut_voir_numero_compte(current_user))


@router.get(
    "/versements",
    summary="Versements de salaire de l'annee scolaire (plus recents en premier), pagines et filtres",
    status_code=200,
    response_model=PaginatedVersementSalaire,
)
def get_versements(
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.CONSULTER))],
    mois: Annotated[int | None, Query(ge=1, le=12, description="Mois paye (avec annee_civile)")] = None,
    annee_civile: Annotated[int | None, Query(description="Annee civile du mois paye (avec mois)")] = None,
    q: Annotated[str | None, Query(max_length=100, description="Nom ou prenom de l'enseignant")] = None,
    id_matiere: Annotated[int | None, Query(description="Id de la matiere enseignee")] = None,
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'elements par page")] = None,
):
    return salaire_service.get_versements(mois, annee_civile, q, id_matiere, page, page_size)


@router.post(
    "/versement",
    summary="Enregistrer un versement de salaire (total ou partiel) pour un mois (refuse si l'enseignant est inactif)",
    status_code=201,
    response_model=VersementSalaireResponseDTO,
)
def verser_salaire(
    data: VersementSalaireCreateDTO,
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.AJOUTER))],
):
    return salaire_service.verser_salaire(data, current_user["user"])


@router.patch(
    "/versement/annuler/{versement_id}",
    summary="Annuler un versement de salaire",
    status_code=200,
    response_model=VersementSalaireResponseDTO,
)
def annuler_versement(
    versement_id: int,
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.ANNULER))],
):
    return salaire_service.annuler_versement(versement_id)


@router.get(
    "/moyens-paiement",
    summary="Moyens de paiement des enseignants actifs (configure=false : pas encore renseignes), pagines",
    status_code=200,
    response_model=PaginatedMoyenPaiement,
)
def get_moyens_paiement(
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.CONSULTER))],
    configure: Annotated[bool | None, Query(description="true : configures, false : non configures, vide : tous")] = None,
    q: Annotated[str | None, Query(max_length=100, description="Nom ou prenom de l'enseignant")] = None,
    id_matiere: Annotated[int | None, Query(description="Id de la matiere enseignee")] = None,
    page: Annotated[int | None, Query(ge=1, description="Page actuelle")] = None,
    page_size: Annotated[int | None, Query(ge=1, le=200, description="Nombre d'elements par page")] = None,
):
    return salaire_service.get_moyens_paiement(
        configure, q, id_matiere, page, page_size, peut_voir_numero_compte(current_user))


@router.patch(
    "/moyen-paiement/{id_enseignant}",
    summary="Configurer le moyen de paiement du salaire d'un enseignant",
    status_code=200,
    response_model=MoyenPaiementEnseignantDTO,
)
def configurer_moyen_paiement(
    id_enseignant: int,
    data: MoyenPaiementUpdateDTO,
    salaire_service: Annotated[SalaireService, Depends(get_salaire_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.SALAIRE, Action.MODIFIER))],
):
    return salaire_service.configurer_moyen_paiement(id_enseignant, data)
