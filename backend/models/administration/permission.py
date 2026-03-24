from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship
from schemas.administration.permission_dto import PermissionBase

if TYPE_CHECKING:
    from models.administration.role import Role


class Permission(PermissionBase, table=True):
    __tablename__ = "permission"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la permission"
    )
    id_role: int = Field(
        sa_column=Column(Integer, ForeignKey("role.id", ondelete="CASCADE")),
        description="Id du rôle associé",
    )

    role: "Role" = Relationship(back_populates="permissions")
