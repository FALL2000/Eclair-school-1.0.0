from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.eleve.eleve_repository import EleveRepository
from schemas.eleve.eleve_dto import EleveResponseDTO, EleveUpdateDTO
from services.eleve.eleve_service import EleveService

router = APIRouter()


def get_eleve_service(db: Session = Depends(get_db)):
    eleve_repo = EleveRepository(db)
    return EleveService(eleve_repo)


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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
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
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return eleve_service.get_all_eleve()
