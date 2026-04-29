from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

from schemas.administration.groupe_matiere_dto import GroupeMatiereBase

if TYPE_CHECKING:
    from models.administration.matiere import Matiere


class GroupeMatiere(GroupeMatiereBase, table=True):
    __tablename__ = "groupe_matiere"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du groupe de matières"
    )

    matieres: list["Matiere"] = Relationship(
        back_populates="groupe_matiere", sa_relationship_kwargs={"cascade": "all, delete"})
