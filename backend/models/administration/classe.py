from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship
from schemas.administration.classe_dto import ClasseBase

if TYPE_CHECKING:
    from models.administration.niveau import Niveau
    from models.inscription.inscription import Inscription
    from models.enseignement.cours import Cours
    from models.evaluations.discipline_eleve import DisciplineEleve
    from models.evaluations.notation import Notation


class Classe(ClasseBase, table=True):
    __tablename__ = "classe"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la classe")
    id_niveau: int = Field(
        sa_column=Column(Integer, ForeignKey("niveau.id", ondelete="CASCADE")),
        description="Id du niveau"
    )

    niveau: "Niveau" = Relationship(back_populates="classes")
    inscriptions: list["Inscription"] = Relationship(back_populates="classe")
    notations: list["Notation"] = Relationship(back_populates="classe")
    cours: list["Cours"] = Relationship(back_populates="classe")
    disciplines: list["DisciplineEleve"] = Relationship(
        back_populates="classe")
