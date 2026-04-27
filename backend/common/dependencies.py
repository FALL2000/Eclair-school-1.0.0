"""Fichier de dépendances pour les routes et fonctions du projet."""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from config.database import engine
from repositories.administration.user_repository import UserRepository
from services.administration.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    """This function starts a db session"""
    with Session(engine) as session:
        yield session


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Retourne le user connecte"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_current_user(token)
