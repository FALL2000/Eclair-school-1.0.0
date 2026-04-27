from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.enseignement.presence_enseignant_dto import (
    PresenceEnseignantBase,
)

if TYPE_CHECKING:
    from models.enseignement.cours import Cours
    from models.enseignants.enseignant import Enseignant


class PresenceEnseignant(PresenceEnseignantBase, table=True):
    __tablename__ = "presence_enseignant"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la présence enseignant(Session de cours)"
    )
    id_cours: int = Field(
        foreign_key="cours.id",
        description="Id du cours",
    )
    id_enseignant: int = Field(
        foreign_key="enseignant.id", description="Id de l'enseignant")

    cours: "Cours" = Relationship(back_populates="presences_enseignant")
    enseignant: "Enseignant" = Relationship(back_populates="presences")
