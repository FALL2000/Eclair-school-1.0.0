from fastapi import Depends, HTTPException

from common.permissions import ROLE_SUPER_ADMIN
from models.administration.user import User
from schemas.administration.user_dto import UserCreateDTO, UserPasswordUpdateDTO, UserUpdateDTO
from security.jwt_handler import decode_token
from security.password_hacher import hash_password, verify_password
from repositories.administration.permission_repository import PermissionRepository
from repositories.administration.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository, permission_repository: PermissionRepository):
        self.user_repository = user_repository
        self.permission_repository = permission_repository

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
            if not user.is_active:
                raise HTTPException(status_code=401, detail={
                    "error_code": "USER_DESACTIVE", "message": "Ce compte utilisateur est désactivé."
                })
            roles = [role.role_name for role in self.permission_repository.find_roles_user(user.id)]
            return {
                "user": user.model_dump(exclude={"password"}),
                "roles": roles,
                "is_super_admin": ROLE_SUPER_ADMIN in roles,
                "permissions": sorted(self.permission_repository.find_codes_user(user.id)),
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du user: {str(e)}")

    def _get_user(self, user_id: int) -> User:
        db_user = self.user_repository.findOne(user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail={
                "error_code": "USER_NOT_FOUND", "message": "Utilisateur non trouvé."
            })
        return db_user

    def _check_droit_sur_super_admin(self, user_id: int, current_user: dict, action: str):
        """Seul un SUPER ADMIN peut modifier ou désactiver un SUPER ADMIN"""
        roles = [role.role_name for role in self.permission_repository.find_roles_user(user_id)]
        if ROLE_SUPER_ADMIN in roles and not current_user["is_super_admin"]:
            raise HTTPException(status_code=403, detail={
                "error_code": "PERMISSION_REFUSEE",
                "message": f"Seul un SUPER ADMIN peut {action} un SUPER ADMIN",
            })

    def get_all_users(self):
        """Récupère tous les utilisateurs"""
        try:
            return self.user_repository.findAll()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des utilisateurs: {str(e)}")

    def update_user(self, user_id: int, user_update: UserUpdateDTO, current_user: dict):
        """Modifie un utilisateur (username, nom, prénom)"""
        try:
            db_user = self._get_user(user_id)
            self._check_droit_sur_super_admin(user_id, current_user, "modifier")
            if user_update.username is not None and user_update.username != db_user.username:
                if self.user_repository.findByUsername(user_update.username):
                    raise HTTPException(status_code=409, detail={
                        "error_code": "DUPLICATE_USERNAME", "message": "username existant"
                    })
            update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            updated = self.user_repository.save(db_user)
            self.user_repository.session.commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du user: {str(e)}")

    def desactiver_user(self, user_id: int, current_user: dict):
        """Désactive un utilisateur : il ne peut plus se connecter"""
        try:
            db_user = self._get_user(user_id)
            if user_id == current_user["user"]["id"]:
                raise HTTPException(status_code=409, detail={
                    "error_code": "DESACTIVATION_SOI_MEME", "message": "Vous ne pouvez pas désactiver votre propre compte."
                })
            self._check_droit_sur_super_admin(user_id, current_user, "désactiver")
            if not db_user.is_active:
                raise HTTPException(status_code=409, detail={
                    "error_code": "USER_DEJA_DESACTIVE", "message": "L'utilisateur est déjà désactivé."
                })
            db_user.is_active = False
            updated = self.user_repository.save(db_user)
            self.user_repository.session.commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la désactivation du user: {str(e)}")

    def change_password(self, current_user: dict, data: UserPasswordUpdateDTO):
        """L'utilisateur connecté change son propre mot de passe (l'ancien mot de passe est exigé)"""
        try:
            db_user = self._get_user(current_user["user"]["id"])
            if not verify_password(data.ancien_mot_de_passe, db_user.password):
                raise HTTPException(status_code=400, detail={
                    "error_code": "MOT_DE_PASSE_INCORRECT", "message": "L'ancien mot de passe est incorrect."
                })
            if data.nouveau_mot_de_passe == data.ancien_mot_de_passe:
                raise HTTPException(status_code=400, detail={
                    "error_code": "MOT_DE_PASSE_IDENTIQUE",
                    "message": "Le nouveau mot de passe doit être différent de l'ancien."
                })
            db_user.password = hash_password(data.nouveau_mot_de_passe)
            self.user_repository.save(db_user)
            self.user_repository.session.commit()
            return {"success": True, "detail": {"message": "Mot de passe modifié"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.user_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du changement de mot de passe: {str(e)}")
