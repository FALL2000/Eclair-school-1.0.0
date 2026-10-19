from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from schemas.evaluations.depends_evaluation_dto import (
    DependsEvaluationBulkCreateDTO,
    DependsEvaluationResponseDTO,
    DependsEvaluationUpdateDTO,
)
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
    depends_evaluation_repo = DependsEvaluationRepository(db)
    return EvaluationService(evaluation_repo, trimestre_repo, depends_evaluation_repo)


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


@router.post(
    "/add-dependances/{evaluation_id}",
    summary="Ajouter des dépendances à une évaluation",
    status_code=201,
    response_model=list[DependsEvaluationResponseDTO],
)
def add_dependances(
    evaluation_id: int,
    data: DependsEvaluationBulkCreateDTO,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.add_dependances(evaluation_id, data)


@router.patch(
    "/update-dependance/{dependance_id}",
    summary="Modifier le pourcentage d'une dépendance",
    status_code=200,
    response_model=DependsEvaluationResponseDTO,
)
def update_dependance(
    dependance_id: int,
    dependance_update: DependsEvaluationUpdateDTO,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.update_dependance(dependance_id, dependance_update)


@router.delete(
    "/delete-dependance/{dependance_id}",
    summary="Supprimer une dépendance",
    status_code=200,
)
def delete_dependance(
    dependance_id: int,
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return evaluation_service.delete_dependance(dependance_id)
