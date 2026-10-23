from fastapi import HTTPException

from common.permissions import ROLE_SUPER_ADMIN
from models.administration.role import Role
from repositories.administration.permission_repository import PermissionRepository
from repositories.administration.role_permission_repository import RolePermissionRepository
from repositories.administration.role_repository import RoleRepository
from repositories.administration.user_repository import UserRepository
from repositories.administration.user_role_repository import UserRoleRepository
from schemas.administration.role_dto import (
    RoleCreateDTO,
    RolePermissionsUpdateDTO,
    RoleUpdateDTO,
    UserRolesUpdateDTO,
)


class RoleService:
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        role_permission_repository: RolePermissionRepository,
        user_role_repository: UserRoleRepository,
        user_repository: UserRepository,
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.role_permission_repository = role_permission_repository
        self.user_role_repository = user_role_repository
        self.user_repository = user_repository

    def _session(self):
        return self.role_repository.session

    def _get_role(self, role_id: int) -> Role:
        db_role = self.role_repository.findOne(role_id)
        if db_role is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "ROLE_NOT_FOUND", "message": "Rôle non trouvé"},
            )
        return db_role

    def _check_role_name_exists(self, role_name: str):
        if len(self.role_repository.findBy(role_name=role_name)) > 0:
            raise HTTPException(
                status_code=409,
                detail={"error_code": "DUPLICATION_ROLE", "message": f"Le rôle {role_name} existe déjà."},
            )

    def _check_non_systeme(self, db_role: Role, action: str):
        if db_role.is_systeme:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "ROLE_SYSTEME",
                    "message": f"Impossible de {action} le rôle de base {db_role.role_name}",
                },
            )

    def _role_detail(self, db_role: Role) -> dict:
        return {
            "id": db_role.id,
            "role_name": db_role.role_name,
            "is_systeme": db_role.is_systeme,
            "permissions": self.permission_repository.find_permissions_role(db_role.id),
        }

    # ---------------- Rôles ----------------

    def get_all_roles(self):
        """Récupère tous les rôles"""
        try:
            return self.role_repository.findAll()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des rôles: {str(e)}")

    def get_one_role(self, role_id: int):
        """Récupère un rôle avec ses permissions"""
        try:
            return self._role_detail(self._get_role(role_id))
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération du rôle: {str(e)}")

    def add_role(self, role_in: RoleCreateDTO):
        """Ajoute un rôle (sans permission : elles s'attribuent ensuite)"""
        try:
            self._check_role_name_exists(role_in.role_name)
            db_role = Role.model_validate(role_in)
            new_role = self.role_repository.save(db_role)
            self._session().commit()
            return new_role
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du rôle: {str(e)}")

    def update_role(self, role_id: int, role_update: RoleUpdateDTO):
        """Renomme un rôle (impossible pour les rôles de base)"""
        try:
            db_role = self._get_role(role_id)
            self._check_non_systeme(db_role, "modifier")
            if role_update.role_name is not None and role_update.role_name != db_role.role_name:
                self._check_role_name_exists(role_update.role_name)
                db_role.role_name = role_update.role_name
            updated = self.role_repository.save(db_role)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du rôle: {str(e)}")

    def delete_role(self, role_id: int):
        """Supprime un rôle (impossible pour les rôles de base) ; ses attributions sont supprimées en cascade"""
        try:
            db_role = self._get_role(role_id)
            self._check_non_systeme(db_role, "supprimer")
            deleted = self.role_repository.deleteOne(role_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": role_id, "message": "Rôle supprimé"}}
            return {"success": False, "detail": {"id": role_id, "message": "Rôle non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du rôle: {str(e)}")

    # ---------------- Permissions ----------------

    def get_all_permissions(self):
        """Catalogue des permissions du système (trié par domaine, module, action)"""
        try:
            return self.permission_repository.find_all_ordered()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des permissions: {str(e)}")

    def update_permissions_role(self, role_id: int, data: RolePermissionsUpdateDTO):
        """Remplace les permissions d'un rôle par la liste fournie"""
        try:
            db_role = self._get_role(role_id)
            if db_role.role_name == ROLE_SUPER_ADMIN:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "ROLE_SUPER_ADMIN",
                        "message": "Le SUPER ADMIN a toutes les permissions : elles ne s'attribuent pas",
                    },
                )
            ids_permissions = set(data.ids_permissions)
            existantes = {p.id for p in self.permission_repository.findAll() if p.id in ids_permissions}
            inconnues = sorted(ids_permissions - existantes)
            if inconnues:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "PERMISSION_NOT_FOUND", "message": f"Permissions inconnues : {inconnues}"},
                )
            actuelles = self.role_permission_repository.findBy(id_role=role_id)
            self.role_permission_repository.deleteMany([rp.id for rp in actuelles])
            self.role_permission_repository.InsertMany(
                [{"id_role": role_id, "id_permission": id_permission} for id_permission in sorted(ids_permissions)])
            self._session().commit()
            return self._role_detail(db_role)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'attribution des permissions: {str(e)}")

    # ---------------- Rôles des utilisateurs ----------------

    def _ids_super_admins(self, id_role_super_admin: int) -> set[int]:
        return {ur.id_user for ur in self.user_role_repository.findBy(id_role=id_role_super_admin)}

    def get_roles_user(self, user_id: int):
        """Rôles d'un utilisateur"""
        try:
            if self.user_repository.findOne(user_id) is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "USER_NOT_FOUND", "message": "Utilisateur non trouvé"},
                )
            return self.permission_repository.find_roles_user(user_id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des rôles de l'utilisateur: {str(e)}")

    def update_roles_user(self, user_id: int, data: UserRolesUpdateDTO, current_user: dict):
        """Remplace les rôles d'un utilisateur par la liste fournie.
        Seul un SUPER ADMIN peut donner ou retirer le rôle SUPER ADMIN,
        et le dernier SUPER ADMIN ne peut pas perdre ce rôle."""
        try:
            if self.user_repository.findOne(user_id) is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "USER_NOT_FOUND", "message": "Utilisateur non trouvé"},
                )
            ids_roles = set(data.ids_roles)
            roles = {r.id: r for r in self.role_repository.findAll()}
            inconnus = sorted(ids_roles - set(roles))
            if inconnus:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "ROLE_NOT_FOUND", "message": f"Rôles inconnus : {inconnus}"},
                )

            role_super_admin = next((r for r in roles.values() if r.role_name == ROLE_SUPER_ADMIN), None)
            if role_super_admin is not None:
                super_admins = self._ids_super_admins(role_super_admin.id)
                etait_super_admin = user_id in super_admins
                sera_super_admin = role_super_admin.id in ids_roles
                if etait_super_admin != sera_super_admin and not current_user["is_super_admin"]:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error_code": "PERMISSION_REFUSEE",
                            "message": "Seul un SUPER ADMIN peut donner ou retirer le rôle SUPER ADMIN",
                        },
                    )
                if etait_super_admin and not sera_super_admin and len(super_admins) == 1:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "DERNIER_SUPER_ADMIN",
                            "message": "Impossible de retirer le rôle SUPER ADMIN au dernier SUPER ADMIN",
                        },
                    )

            actuels = self.user_role_repository.findBy(id_user=user_id)
            self.user_role_repository.deleteMany([ur.id for ur in actuels])
            self.user_role_repository.InsertMany(
                [{"id_user": user_id, "id_role": id_role} for id_role in sorted(ids_roles)])
            self._session().commit()
            return self.permission_repository.find_roles_user(user_id)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'attribution des rôles: {str(e)}")
