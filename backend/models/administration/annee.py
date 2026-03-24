from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.administration.annee_dto import AnneeBase

if TYPE_CHECKING:
    from models.enseignement.cours import Cours
    from models.evaluations.discipline_eleve import DisciplineEleve
    from models.evaluations.notation import Notation
    from models.inscription.inscription import Inscription
    from models.scolarite.reglement import Reglement


class Annee(AnneeBase, table=True):
    __tablename__ = "annee"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'annee scolaire")
    is_cloture: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'annee est cloture",
    )

    inscriptions: list["Inscription"] = Relationship(back_populates="annee")
    reglements: list["Reglement"] = Relationship(back_populates="annee")
    cours: list["Cours"] = Relationship(back_populates="annee")
    notations: list["Notation"] = Relationship(back_populates="annee")
    disciplines: list["DisciplineEleve"] = Relationship(back_populates="annee")
