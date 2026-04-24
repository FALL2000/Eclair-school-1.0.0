from fastapi import Depends, HTTPException

from models.administration.user import User
from schemas.administration.user_dto import UserCreateDTO
from security.jwt_handler import decode_token
from security.password_hacher import hash_password
from repositories.administration.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def add_user(self, user_in: UserCreateDTO):
        """Ajoute un nouvel utilisateur au systeme"""
        try:
            if self.user_repository.findByUsername(user_in.username):
                raise HTTPException(status_code=409, detail={
                    "error_code": "DUPLICATE_USERNAME", "message": "username existant"
                })
            db_user = User.model_validate(user_in)
            db_user.password = hash_password(user_in.password)
            new_user = self.user_repository.save(db_user)
            self.user_repository.session.commit()
            return new_user
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la sauvegarde du user: {str(e)}")

    def get_current_user(self, token: str):
        try:
            payload = decode_token(token)
            if not payload or payload.get("type") != "access":
                raise HTTPException(status_code=401, detail={
                    "error_code": "INVALID_TOKEN_ACCESS", "message": "Token d'accès invalide."
                })
            user = self.user_repository.findOne(payload["sub"])
            if not user:
                raise HTTPException(status_code=404, detail={
                    "error_code": "USER_NOT_FOUND", "message": "Utilisateur non trouvé."
                })
            return {
                "user": user.model_dump(exclude={"password"}),
                "is_admin": True
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du user: {str(e)}")
