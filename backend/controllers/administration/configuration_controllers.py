from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import check_permission_user, get_db
from repositories.administration.configuration_repository import ConfigurationRepository
from schemas.administration.configuration_dto import (
    ConfigurationCreateDTO,
    ConfigurationResponseDTO,
    ConfigurationUpdateDTO,
)
from services.administration.configuration_service import ConfigurationService

router = APIRouter()


def get_configuration_service(db: Session = Depends(get_db)):
    configuration_repo = ConfigurationRepository(db)
    return ConfigurationService(configuration_repo)


@router.post(
    "/add",
    summary="Ajouter une configuration",
    status_code=201,
    response_model=ConfigurationResponseDTO,
)
def add_configuration(
    configuration_in: ConfigurationCreateDTO,
    configuration_service: Annotated[ConfigurationService, Depends(get_configuration_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return configuration_service.add_configuration(configuration_in)


@router.patch(
    "/update/{configuration_id}",
    summary="Modifier une configuration",
    status_code=200,
    response_model=ConfigurationResponseDTO,
)
def update_configuration(
    configuration_id: int,
    configuration_update: ConfigurationUpdateDTO,
    configuration_service: Annotated[ConfigurationService, Depends(get_configuration_service)],
    _: Annotated[dict[str, Any], Depends(check_permission_user)],
):
    return configuration_service.update_configuration(configuration_id, configuration_update)
