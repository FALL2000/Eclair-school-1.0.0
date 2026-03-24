from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING
from schemas.eleve.eleve_dto import EleveBase

if TYPE_CHECKING:
    from models.inscription.inscription import Inscription
    from models.enseignement.presence_eleve import PresenceEleve
    from models.evaluations.discipline_eleve import DisciplineEleve
    from models.evaluations.notation import Notation
    from models.scolarite.reglement import Reglement


class Eleve(EleveBase, table=True):
    __tablename__ = "eleve"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'eleve")
    matricule: str = Field(
        unique=True, max_length=8, description="Matricule de l'eleve", nullable=False)
    is_active: bool = Field(default=True,  nullable=False,  sa_column_kwargs={
                            "server_default": "1"}, description="Indique si l'élève est actuellement actif dans l'établissement")

    inscriptions: list["Inscription"] = Relationship(back_populates="eleve")
    reglements: list["Reglement"] = Relationship(back_populates="eleve")
    notations: list["Notation"] = Relationship(back_populates="eleve")
    presences: list["PresenceEleve"] = Relationship(back_populates="eleve")
    disciplines: list["DisciplineEleve"] = Relationship(back_populates="eleve")
