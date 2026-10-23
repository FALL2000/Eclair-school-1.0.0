"""Fichier de dépendances pour les routes et fonctions du projet."""
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from common.permissions import Action, Module, code_permission
from config.database import engine
from repositories.administration.permission_repository import PermissionRepository
from repositories.administration.user_repository import UserRepository
from services.administration.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    """This function starts a db session"""
    with Session(engine) as session:
        yield session


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Retourne le user connecte avec ses rôles et ses permissions"""
    user_service = UserService(UserRepository(db), PermissionRepository(db))
    return user_service.get_current_user(token)


def require_permission(module: Module, action: Action):
    """Dépendance qui vérifie que l'utilisateur connecté a la permission « module:action ».
    Le SUPER ADMIN a toutes les permissions. Retourne l'utilisateur connecté.
    Usage : _: Annotated[dict[str, Any], Depends(require_permission(Module.ELEVE, Action.INSCRIRE))]"""
    code = code_permission(module, action)

    def verifier_permission(current_user: dict[str, Any] = Depends(get_current_user)):
        if current_user["is_super_admin"] or code in current_user["permissions"]:
            return current_user
        raise HTTPException(
            status_code=403,
            detail={
                "error_code": "PERMISSION_REFUSEE",
                "message": f"Vous n'avez pas la permission d'effectuer cette action ({code})",
            },
        )

    return verifier_permission


def require_super_admin(current_user: dict[str, Any] = Depends(get_current_user)):
    """Dépendance réservant une action au SUPER ADMIN"""
    if not current_user["is_super_admin"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error_code": "PERMISSION_REFUSEE",
                "message": "Action réservée au SUPER ADMIN",
            },
        )
    return current_user
