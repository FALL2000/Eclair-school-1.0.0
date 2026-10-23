from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_current_user, get_db, require_permission
from common.permissions import Action, Module
from repositories.administration.permission_repository import PermissionRepository
from repositories.administration.user_repository import UserRepository
from schemas.administration.user_dto import (
    UserCreateDTO,
    UserPasswordUpdateDTO,
    UserResponseDTO,
    UserUpdateDTO,
)
from services.administration.user_service import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    permission_repo = PermissionRepository(db)
    return UserService(user_repo, permission_repo)


@router.post(
    "/register",
    summary="Enregistrer un nouvel utilisateur",
    status_code=201,
    response_model=UserResponseDTO
)
def register(
    user_in: UserCreateDTO,
    user_service: Annotated[UserService, Depends(get_user_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.UTILISATEUR, Action.AJOUTER))],
):
    """
    Les codes de response:
    201: Utilisateur enregistre avec succes
    400-422: Mauvaise requete(format de donnee invalide, donnees ne respectant le format attendu)
    403: user ne dispose pas les droits pour l'action
    409: duplication de username(utilisation de username existant)
    500: Erreur interne au serveur
    """
    return user_service.add_user(user_in)


@router.get(
    "/me",
    summary="Récupérer l'utilisateur connecté",
    response_model=None,
    status_code=200
)
def read_user_me(current_user: Annotated[dict[str, Any], Depends(get_current_user)]):
    """
    Les codes de response:
    200: succes
    401: Token Invalide
    500: Erreur interne au serveur
    """
    return current_user


@router.patch(
    "/password",
    summary="Changer son propre mot de passe",
    status_code=200,
)
def change_password(
    data: UserPasswordUpdateDTO,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
):
    return user_service.change_password(current_user, data)


@router.get(
    "/all",
    summary="Lister les utilisateurs",
    status_code=200,
    response_model=list[UserResponseDTO],
)
def get_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.UTILISATEUR, Action.CONSULTER))],
):
    return user_service.get_all_users()


@router.patch(
    "/update/{user_id}",
    summary="Modifier un utilisateur",
    status_code=200,
    response_model=UserResponseDTO,
)
def update_user(
    user_id: int,
    user_update: UserUpdateDTO,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.UTILISATEUR, Action.MODIFIER))],
):
    return user_service.update_user(user_id, user_update, current_user)


@router.patch(
    "/desactiver/{user_id}",
    summary="Désactiver un utilisateur (il ne peut plus se connecter)",
    status_code=200,
    response_model=UserResponseDTO,
)
def desactiver_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[dict[str, Any], Depends(require_permission(Module.UTILISATEUR, Action.SUPPRIMER))],
):
    return user_service.desactiver_user(user_id, current_user)
