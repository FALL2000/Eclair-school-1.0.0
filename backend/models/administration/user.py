from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.user_dto import UserBase

if TYPE_CHECKING:
    from models.administration.user_role import UserRole


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'utilisateur"
    )
    password: str = Field(
        max_length=128,
        description="Mot de passe (hashé)",
        nullable=False,
    )

    user_roles: list["UserRole"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"})
