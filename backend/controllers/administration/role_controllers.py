from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.permission_repository import PermissionRepository
from repositories.administration.role_permission_repository import RolePermissionRepository
from repositories.administration.role_repository import RoleRepository
from repositories.administration.user_repository import UserRepository
from repositories.administration.user_role_repository import UserRoleRepository
from schemas.administration.permission_dto import PermissionResponseDTO
from schemas.administration.role_dto import (
    RoleCreateDTO,
    RoleDetailResponseDTO,
    RolePermissionsUpdateDTO,
    RoleResponseDTO,
    RoleUpdateDTO,
    UserRolesUpdateDTO,
)
from services.administration.role_service import RoleService

router = APIRouter()


def get_role_service(db: Session = Depends(get_db)):
    return RoleService(
        RoleRepository(db),
        PermissionRepository(db),
        RolePermissionRepository(db),
        UserRoleRepository(db),
        UserRepository(db),
    )


@router.get(
    "/all",
    summary="Recuperer tous les rôles",
    status_code=200,
    response_model=list[RoleResponseDTO],
)
def get_all_roles(
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.CONSULTER))],
):
    return role_service.get_all_roles()


@router.get(
    "/one/{role_id}",
    summary="Recuperer un rôle avec ses permissions",
    status_code=200,
    response_model=RoleDetailResponseDTO,
)
def get_one_role(
    role_id: int,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.CONSULTER))],
):
    return role_service.get_one_role(role_id)


@router.post(
    "/add",
    summary="Ajouter un rôle",
    status_code=201,
    response_model=RoleResponseDTO,
)
def add_role(
    role_in: RoleCreateDTO,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.AJOUTER))],
):
    return role_service.add_role(role_in)


@router.patch(
    "/update/{role_id}",
    summary="Renommer un rôle",
    status_code=200,
    response_model=RoleResponseDTO,
)
def update_role(
    role_id: int,
    role_update: RoleUpdateDTO,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.MODIFIER))],
):
    return role_service.update_role(role_id, role_update)


@router.delete(
    "/delete/{role_id}",
    summary="Supprimer un rôle",
    status_code=200,
)
def delete_role(
    role_id: int,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.SUPPRIMER))],
):
    return role_service.delete_role(role_id)


@router.get(
    "/permissions",
    summary="Recuperer le catalogue des permissions du système",
    status_code=200,
    response_model=list[PermissionResponseDTO],
)
def get_all_permissions(
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.CONSULTER))],
):
    return role_service.get_all_permissions()


@router.put(
    "/permissions/{role_id}",
    summary="Définir les permissions d'un rôle (remplace les permissions actuelles)",
    status_code=200,
    response_model=RoleDetailResponseDTO,
)
def update_permissions_role(
    role_id: int,
    data: RolePermissionsUpdateDTO,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.ATTRIBUER))],
):
    return role_service.update_permissions_role(role_id, data)


@router.get(
    "/user/{user_id}",
    summary="Recuperer les rôles d'un utilisateur",
    status_code=200,
    response_model=list[RoleResponseDTO],
)
def get_roles_user(
    user_id: int,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.CONSULTER))],
):
    return role_service.get_roles_user(user_id)


@router.put(
    "/user/{user_id}",
    summary="Définir les rôles d'un utilisateur (remplace les rôles actuels)",
    status_code=200,
    response_model=list[RoleResponseDTO],
)
def update_roles_user(
    user_id: int,
    data: UserRolesUpdateDTO,
    role_service: Annotated[RoleService, Depends(get_role_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.ROLE, Action.ATTRIBUER))],
):
    return role_service.update_roles_user(user_id, data, current_user)
