from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.inscription.inscription_dto import InscriptionBase

if TYPE_CHECKING:
    from models.administration.annee import Annee
    from models.administration.classe import Classe
    from models.eleve.eleve import Eleve


class Inscription(InscriptionBase, table=True):
    __tablename__ = "inscription"

    __table_args__ = (
        UniqueConstraint("id_eleve", "id_classe", "id_annee",
                         name="unique_inscription_eleve_annee"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'inscription")
    id_eleve: int = Field(
        foreign_key="eleve.id",
        description="Id de l'eleve"
    )
    id_classe: int = Field(
        foreign_key="classe.id",
        description="Id de la classe"
    )
    id_annee: int = Field(foreign_key="annee.id", description="Id de l'annee")
    date_inscris: date = Field(description="Date d'inscription de l'eleve")

    eleve: "Eleve" = Relationship(back_populates="inscriptions")
    classe: "Classe" = Relationship(back_populates="inscriptions")
    annee: "Annee" = Relationship(back_populates="inscriptions")
