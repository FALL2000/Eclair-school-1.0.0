from typing import Optional

from sqlmodel import Field, SQLModel

from schemas.administration.permission_dto import PermissionResponseDTO


class RoleBase(SQLModel):
    role_name: str = Field(
        unique=True,
        max_length=50,
        description="Nom du rôle (ADMIN, PROF, etc.)",
        nullable=False,
    )


class RoleCreateDTO(RoleBase):
    pass


class RoleUpdateDTO(SQLModel):
    role_name: Optional[str] = None


class RoleResponseDTO(RoleBase):
    id: int
    is_systeme: bool


class RoleDetailResponseDTO(RoleResponseDTO):
    permissions: list[PermissionResponseDTO]


class RolePermissionsUpdateDTO(SQLModel):
    """Liste complète des permissions du rôle (remplace les permissions actuelles)"""
    ids_permissions: list[int]


class UserRolesUpdateDTO(SQLModel):
    """Liste complète des rôles de l'utilisateur (remplace les rôles actuels)"""
    ids_roles: list[int]
