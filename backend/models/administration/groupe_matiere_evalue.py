from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship


from schemas.administration.groupe_matiere_evalues_dto import GroupeMatiereEvalueBase

if TYPE_CHECKING:
    from models.administration.matiere_evalue import MatiereEvalue
    from models.administration.niveau import Niveau


class GroupeMatiereEvalue(GroupeMatiereEvalueBase, table=True):
    __tablename__ = "groupe_matiere_evalue"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du groupe de matières evaluées"
    )
    id_niveau: int = Field(
        sa_column=Column(Integer, ForeignKey("niveau.id", ondelete="CASCADE")),
        description="Id du niveau",
    )

    niveau: "Niveau" = Relationship(back_populates="groupe_matiere_evaluees")
    matiere_evalues: list["MatiereEvalue"] = Relationship(
        back_populates="groupe_matiere", sa_relationship_kwargs={"cascade": "all, delete"})
