from datetime import time
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.enseignement.cours_dto import CoursBase

if TYPE_CHECKING:
    from models.enseignants.enseignant import Enseignant
    from models.administration.classe import Classe
    from models.administration.annee import Annee
    from models.administration.matiere import Matiere
    from models.enseignement.presence_enseignant import PresenceEnseignant
    from models.enseignement.presence_eleve import PresenceEleve


class Cours(CoursBase, table=True):
    __tablename__ = "cours"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du cours"
    )
    id_enseignant: int = Field(
        foreign_key="enseignant.id",
        description="Id de l'enseignant",
    )
    id_classe: int = Field(
        foreign_key="classe.id",
        description="Id de la classe",
    )
    id_annee: int = Field(
        foreign_key="annee.id",
        description="Id de l'année scolaire",
    )
    id_matiere: int = Field(
        foreign_key="matiere.id",
        description="Id de la matière",
    )

    enseignant: "Enseignant" = Relationship(back_populates="cours")
    classe: "Classe" = Relationship(back_populates="cours")
    annee: "Annee" = Relationship(back_populates="cours")
    matiere: "Matiere" = Relationship(back_populates="cours")
    presences_enseignant: list["PresenceEnseignant"] = Relationship(
        back_populates="cours"
    )
    presences_eleves: list["PresenceEleve"] = Relationship(
        back_populates="cours"
    )
