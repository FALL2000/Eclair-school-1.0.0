from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.role_dto import RoleBase

if TYPE_CHECKING:
    from administration.user_role import UserRole
    from administration.permission import Permission


class Role(RoleBase, table=True):
    __tablename__ = "role"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du rôle"
    )

    roles_user: list["UserRole"] = Relationship(back_populates="role",
                                                sa_relationship_kwargs={"cascade": "all, delete"})
    permissions: list["Permission"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"cascade": "all, delete"})
