from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from repositories.enseignement.presence_eleve_repository import PresenceEleveRepository
from repositories.evaluations.discipline_eleve_repository import DisciplineEleveRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.discipline_eleve_dto import (
    DisciplineEleveBulkCreateDTO,
    DisciplineEleveBulkUpdateDTO,
    DisciplineEleveCreateDTO,
    DisciplineEleveResponseDTO,
    DisciplineEleveUpdateDTO,
)
from services.evaluations.discipline_eleve_service import DisciplineEleveService

router = APIRouter()


def get_discipline_service(db: Session = Depends(get_db)):
    discipline_repo = DisciplineEleveRepository(db)
    evaluation_repo = EvaluationRepository(db)
    inscription_repo = InscriptionRepository(db)
    presence_eleve_repo = PresenceEleveRepository(db)
    configuration_repo = ConfigurationRepository(db)
    annee_repo = AnneeRepository(db)
    discipline_decision_repo = DisciplineDecisionRepository(db)
    return DisciplineEleveService(
        discipline_repo, evaluation_repo, inscription_repo,
        presence_eleve_repo, configuration_repo, annee_repo,
        discipline_decision_repo,
    )


@router.post(
    "/add",
    summary="Ajouter manuellement la discipline d'un élève (appel désactivé)",
    status_code=201,
    response_model=DisciplineEleveResponseDTO,
)
def add_discipline(
    discipline_in: DisciplineEleveCreateDTO,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.AJOUTER))],
    id_eleve: Annotated[int, Query(description="Id de l'élève")] = ...,
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation")] = ...,
):
    return discipline_service.add_discipline(discipline_in, id_eleve, id_classe, id_evaluation)


@router.post(
    "/add-bulk",
    summary="Ajouter manuellement en masse les disciplines des élèves d'une classe (appel désactivé)",
    status_code=201,
    response_model=list[DisciplineEleveResponseDTO],
)
def add_bulk_disciplines(
    data: DisciplineEleveBulkCreateDTO,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.AJOUTER))],
):
    return discipline_service.add_bulk_disciplines(data)


@router.patch(
    "/update/{discipline_id}",
    summary="Modifier manuellement la discipline d'un élève (appel désactivé)",
    status_code=200,
    response_model=DisciplineEleveResponseDTO,
)
def update_discipline(
    discipline_id: int,
    discipline_update: DisciplineEleveUpdateDTO,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.MODIFIER))],
):
    return discipline_service.update_discipline(discipline_id, discipline_update)


@router.patch(
    "/update-bulk",
    summary="Modifier manuellement en masse les disciplines des élèves (appel désactivé)",
    status_code=200,
    response_model=list[DisciplineEleveResponseDTO],
)
def update_bulk_disciplines(
    data: DisciplineEleveBulkUpdateDTO,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.MODIFIER))],
):
    return discipline_service.update_bulk_disciplines(data)


@router.post(
    "/calculer-eleve/{id_eleve}",
    summary="Calculer et enregistrer automatiquement la discipline d'un élève à partir des présences (appel activé)",
    status_code=200,
    response_model=DisciplineEleveResponseDTO,
)
def calculer_discipline_eleve(
    id_eleve: int,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.CALCULER))],
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation")] = ...,
):
    return discipline_service.calculer_discipline_eleve(id_eleve, id_classe, id_evaluation)


@router.post(
    "/calculer-classe/{id_classe}",
    summary="Calculer et enregistrer automatiquement les disciplines des élèves d'une classe à partir des présences (appel activé)",
    status_code=200,
    response_model=list[DisciplineEleveResponseDTO],
)
def calculer_disciplines_classe(
    id_classe: int,
    discipline_service: Annotated[DisciplineEleveService, Depends(get_discipline_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_ELEVE, Action.CALCULER))],
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation")] = ...,
):
    return discipline_service.calculer_disciplines_classe(id_classe, id_evaluation)
