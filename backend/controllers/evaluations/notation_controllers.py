from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.appreciation_repository import AppreciationRepository
from repositories.administration.bareme_repository import BaremeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.evaluations.notation_repository import NotationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.notation_dto import (
    NotationBulkCreateDTO,
    NotationBulkUpdateDTO,
    NotationCalculResponseDTO,
    NotationDetailResponseDTO,
)
from services.evaluations.notation_service import NotationService

router = APIRouter()


def get_notation_service(db: Session = Depends(get_db)):
    return NotationService(
        NotationRepository(db),
        EvaluationRepository(db),
        ClasseRepository(db),
        MatiereEvalueRepository(db),
        GroupeMatiereEvalueRepository(db),
        BaremeRepository(db),
        AppreciationRepository(db),
        InscriptionRepository(db),
        AnneeRepository(db),
        DependsEvaluationRepository(db),
    )


@router.get(
    "/list",
    summary="Récupérer les notes d'une classe pour une évaluation et une matière évaluée (année en cours)",
    status_code=200,
    response_model=list[NotationDetailResponseDTO],
)
def get_notations(
    notation_service: Annotated[NotationService, Depends(get_notation_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.NOTATION, Action.CONSULTER))],
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation")] = ...,
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_matiere_evalue: Annotated[int, Query(description="Id de la matière évaluée")] = ...,
):
    return notation_service.get_notations(id_evaluation, id_classe, id_matiere_evalue)


@router.post(
    "/add-bulk",
    summary="Enregistrer en masse les notes d'une classe pour une évaluation et une matière évaluée (année en cours)",
    status_code=201,
    response_model=list[NotationDetailResponseDTO],
)
def add_bulk_notations(
    data: NotationBulkCreateDTO,
    notation_service: Annotated[NotationService, Depends(get_notation_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.NOTATION, Action.AJOUTER))],
):
    return notation_service.add_bulk_notations(data)


@router.patch(
    "/update-bulk",
    summary="Modifier en masse les notes d'une classe pour une évaluation et une matière évaluée (année en cours)",
    status_code=200,
    response_model=list[NotationDetailResponseDTO],
)
def update_bulk_notations(
    data: NotationBulkUpdateDTO,
    notation_service: Annotated[NotationService, Depends(get_notation_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.NOTATION, Action.MODIFIER))],
):
    return notation_service.update_bulk_notations(data)


@router.post(
    "/calculer",
    summary="Calculer et enregistrer les notes d'une évaluation à partir de ses dépendances (année en cours)",
    status_code=200,
    response_model=NotationCalculResponseDTO,
)
def calculer_notations(
    notation_service: Annotated[NotationService, Depends(get_notation_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.NOTATION, Action.CALCULER))],
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation qui a des dépendances")] = ...,
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_matiere_evalue: Annotated[int, Query(description="Id de la matière évaluée")] = ...,
):
    return notation_service.calculer_notations(id_evaluation, id_classe, id_matiere_evalue)
