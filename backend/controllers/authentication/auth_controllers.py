from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from common.dependencies import get_db
from repositories.administration.user_repository import UserRepository
from services.authentication.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return AuthService(user_repo)


@router.post(
    "/login",
    summary="Se connecter et obtenir les tokens",
    response_model=None,
    status_code=200
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """
    Les codes de response:
    200: Login reussi
    401: Credentials incorrecte
    500: Erreur Interne au serveur
    """
    return auth_service.login(form_data)


@router.post(
    "/refresh",
    summary="Renouveler l'Access Token via le Refresh Token",
    response_model=None,
    status_code=200
)
def refresh_access_token(refresh_token: str, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """
    Les codes de response:
    200: Refresh reussi
    401: Token Invalide ou expire
    500: Erreur Interne au serveur
    """
    return auth_service.refresh_token(refresh_token)
