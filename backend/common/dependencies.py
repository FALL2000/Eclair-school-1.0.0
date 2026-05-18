"""Fichier de dépendances pour les routes et fonctions du projet."""
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from config.database import engine
from repositories.administration.user_repository import UserRepository
from services.administration.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    """This function starts a db session"""
    with Session(engine) as session:
        yield session


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Retourne le user connecte"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_current_user(token)


def check_permission_user(current_user: dict[str, Any] = Depends(get_current_user)):
    return current_user
