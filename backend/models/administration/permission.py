from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.permission_dto import PermissionBase

if TYPE_CHECKING:
    from models.administration.role_permission import RolePermission


class Permission(PermissionBase, table=True):
    """Catalogue des permissions du système (alimenté par migration)"""
    __tablename__ = "permission"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la permission"
    )

    roles_permission: list["RolePermission"] = Relationship(
        back_populates="permission", sa_relationship_kwargs={"passive_deletes": True})
