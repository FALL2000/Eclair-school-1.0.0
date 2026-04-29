from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.section_repository import SectionRepository
from schemas.administration.section_dto import SectionCreateDTO, SectionResponseDTO, SectionUpdateDTO
from services.administration.section_service import SectionService

router = APIRouter()


def get_section_service(db: Session = Depends(get_db)):
    section_repo = SectionRepository(db)
    annee_repo = AnneeRepository(db)
    return SectionService(section_repo, annee_repo)


@router.post(
    "/add",
    summary="Ajouter une section",
    status_code=201,
    response_model=SectionResponseDTO,
)
def add_section(
    section_in: SectionCreateDTO,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return section_service.add_section(section_in)


@router.patch(
    "/update/{section_id}",
    summary="Modifier une section",
    status_code=200,
    response_model=SectionResponseDTO,
)
def update_section(
    section_id: int,
    section_update: SectionUpdateDTO,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return section_service.update_section(section_update, section_id)


@router.delete(
    "/delete/{section_id}",
    summary="Supprimer une section",
    status_code=200,
)
def delete_section(
    section_id: int,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return section_service.delete_section(section_id)


@router.get(
    "/{section_id}",
    summary="Recuperer une section",
    status_code=200,
    response_model=SectionResponseDTO,
)
def get_one_section(
    section_id: int,
    section_service: Annotated[SectionService, Depends(get_section_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return section_service.get_one_section(section_id)


@router.get(
    "/all",
    summary="Recuperer toutes les sections",
    status_code=200,
    response_model=list[SectionResponseDTO],
)
def get_all_section(
    section_service: Annotated[SectionService, Depends(get_section_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return section_service.get_all_section()
