from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from security.jwt_handler import create_tokens, decode_token
from security.password_hacher import verify_password
from repositories.administration.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        """Login de l'utilisateur"""
        try:
            user = self.user_repository.findByUsername(form_data.username)
            if not user or not verify_password(form_data.password, user[0].password):
                raise HTTPException(status_code=401, detail={
                    "error_code": "INCORRECT_CREDENTIALS", "message": "Email ou mot de passe incorrect."
                })
            return create_tokens(user[0].id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du login du user: {str(e)}")

    def refresh_token(self, refresh_token: str):
        """Rafraichi le token a partir du refresh du token"""
        try:
            payload = decode_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=401, detail="Refresh token invalide ou expiré.")
            return create_tokens(payload["sub"])
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du rafraichissement: {str(e)}")
