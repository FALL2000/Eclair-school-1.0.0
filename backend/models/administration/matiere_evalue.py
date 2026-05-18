from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship

from schemas.administration.matiere_evalue_dto import MatiereEvalueBase

if TYPE_CHECKING:
    from models.administration.groupe_matiere_evalue import GroupeMatiereEvalue
    from models.evaluations.notation import Notation


class MatiereEvalue(MatiereEvalueBase, table=True):
    __tablename__ = "matiere_evalue"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la matière évaluée"
    )
    id_groupe_matiere: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "groupe_matiere_evalue.id", ondelete="CASCADE")),
        description="Id du groupe de matière évaluée"
    )

    groupe_matiere: "GroupeMatiereEvalue" = Relationship(
        back_populates="matiere_evalues")
    notations: list["Notation"] = Relationship(back_populates="matiere_evalue")
