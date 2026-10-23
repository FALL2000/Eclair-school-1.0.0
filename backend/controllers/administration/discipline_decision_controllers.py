from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from repositories.evaluations.discipline_eleve_repository import DisciplineEleveRepository
from schemas.administration.discipline_decision_dto import (
    DisciplineDecisionCreateDTO,
    DisciplineDecisionResponseDTO,
    DisciplineDecisionUpdateDTO,
)
from services.administration.discipline_decision_service import DisciplineDecisionService

router = APIRouter()


def get_discipline_decision_service(db: Session = Depends(get_db)):
    discipline_decision_repo = DisciplineDecisionRepository(db)
    annee_repo = AnneeRepository(db)
    discipline_eleve_repo = DisciplineEleveRepository(db)
    return DisciplineDecisionService(discipline_decision_repo, annee_repo, discipline_eleve_repo)


@router.post(
    "/add",
    summary="Ajouter une décision disciplinaire",
    status_code=201,
    response_model=DisciplineDecisionResponseDTO,
)
def add_decision(
    decision_in: DisciplineDecisionCreateDTO,
    decision_service: Annotated[DisciplineDecisionService, Depends(get_discipline_decision_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_DECISION, Action.AJOUTER))],
):
    return decision_service.add_decision(decision_in)


@router.patch(
    "/update/{decision_id}",
    summary="Modifier une décision disciplinaire",
    status_code=200,
    response_model=DisciplineDecisionResponseDTO,
)
def update_decision(
    decision_id: int,
    decision_update: DisciplineDecisionUpdateDTO,
    decision_service: Annotated[DisciplineDecisionService, Depends(get_discipline_decision_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_DECISION, Action.MODIFIER))],
):
    return decision_service.update_decision(decision_update, decision_id)


@router.delete(
    "/delete/{decision_id}",
    summary="Supprimer une décision disciplinaire",
    status_code=200,
)
def delete_decision(
    decision_id: int,
    decision_service: Annotated[DisciplineDecisionService, Depends(get_discipline_decision_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_DECISION, Action.SUPPRIMER))],
):
    return decision_service.delete_decision(decision_id)


@router.get(
    "/one/{decision_id}",
    summary="Recuperer une décision disciplinaire",
    status_code=200,
    response_model=DisciplineDecisionResponseDTO,
)
def get_one_decision(
    decision_id: int,
    decision_service: Annotated[DisciplineDecisionService, Depends(get_discipline_decision_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_DECISION, Action.CONSULTER))],
):
    return decision_service.get_one_decision(decision_id)


@router.get(
    "/all",
    summary="Recuperer toutes les décisions disciplinaires",
    status_code=200,
    response_model=list[DisciplineDecisionResponseDTO],
)
def get_all_decisions(
    decision_service: Annotated[DisciplineDecisionService, Depends(get_discipline_decision_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.DISCIPLINE_DECISION, Action.CONSULTER))],
):
    return decision_service.get_all_decisions()
