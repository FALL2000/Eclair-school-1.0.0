from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.dependencies import get_current_user, get_db
from repositories.administration.user_repository import UserRepository
from schemas.administration.user_dto import UserCreateDTO, UserResponseDTO
from services.administration.user_service import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserService(user_repo)


@router.post(
    "/register",
    summary="Enregistrer un nouvel utilisateur",
    status_code=201,
    response_model=UserResponseDTO
)
def register(user_in: UserCreateDTO, user_service: Annotated[UserService, Depends(get_user_service)]):
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
