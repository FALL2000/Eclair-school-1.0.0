from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship
from schemas.administration.matiere_evalue_dto import MatiereEvalueBase

if TYPE_CHECKING:
    from administration.niveau import Niveau
    from evaluations.notation import Notation


class MatiereEvalue(MatiereEvalueBase, table=True):
    __tablename__ = "matiere_evalue"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la matière évaluée"
    )
    id_niveau: int = Field(
        sa_column=Column(Integer, ForeignKey("niveau.id", ondelete="CASCADE")),
        description="Id du niveau",
    )

    niveau: "Niveau" = Relationship(back_populates="matieres_evaluees")
    notations: list["Notation"] = Relationship(back_populates="matiere_evalue")
