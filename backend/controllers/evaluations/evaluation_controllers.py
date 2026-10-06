from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from schemas.evaluations.evaluation_dto import (
    EvaluationCreateDTO,
    EvaluationResponseDTO,
    EvaluationUpdateDTO,
)
from services.evaluations.evaluation_service import EvaluationService

router = APIRouter()


def get_evaluation_service(db: Session = Depends(get_db)):
    evaluation_repo = EvaluationRepository(db)
    trimestre_repo = TrimestreRepository(db)
    return EvaluationService(evaluation_repo, trimestre_repo)


@router.post(
    "/add",
    summary="Ajouter une évaluation",
    status_code=201,
    response_model=EvaluationResponseDTO,
)
def add_evaluation(
    evaluation_in: EvaluationCreateDTO,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_trimestre: Annotated[int, Query(description="Id du trimestre auquel appartient l'évaluation")] = ...,
):
    return evaluation_service.add_evaluation(evaluation_in, id_trimestre)


@router.patch(
    "/update/{evaluation_id}",
    summary="Modifier une évaluation",
    status_code=200,
    response_model=EvaluationResponseDTO,
)
def update_evaluation(
    evaluation_id: int,
    evaluation_update: EvaluationUpdateDTO,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.update_evaluation(evaluation_id, evaluation_update)


@router.delete(
    "/delete/{evaluation_id}",
    summary="Supprimer une évaluation",
    status_code=200,
)
def delete_evaluation(
    evaluation_id: int,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.delete_evaluation(evaluation_id)


@router.get(
    "/one/{evaluation_id}",
    summary="Recuperer une évaluation",
    status_code=200,
    response_model=EvaluationResponseDTO,
)
def get_one_evaluation(
    evaluation_id: int,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.get_one_evaluation(evaluation_id)


@router.get(
    "/all",
    summary="Recuperer toutes les évaluations",
    status_code=200,
    response_model=list[EvaluationResponseDTO],
)
def get_all_evaluations(
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
    id_trimestre: Annotated[int | None, Query(description="Filtrer par trimestre (optionnel)")] = None,
):
    return evaluation_service.get_all_evaluations(id_trimestre)
