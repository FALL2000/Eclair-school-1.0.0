from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.enseignement.enseignement_dto import EnseignementBase

if TYPE_CHECKING:
    from models.enseignants.enseignant import Enseignant
    from models.administration.matiere import Matiere


class Enseignement(EnseignementBase, table=True):
    __tablename__ = "enseignement"

    __table_args__ = (
        UniqueConstraint("id_enseignant", "id_matiere",
                         name="unique_enseignant_matiere"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'enseignement"
    )
    id_enseignant: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "enseignant.id", ondelete="CASCADE")),
        description="Id de l'enseignant",
    )
    id_matiere: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "matiere.id", ondelete="CASCADE")),
        description="Id de la matière",
    )

    enseignant: "Enseignant" = Relationship(back_populates="enseignements")
    matiere: "Matiere" = Relationship(back_populates="enseignements")
