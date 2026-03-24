from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.enseignement.presence_eleve_dto import PresenceEleveBase

if TYPE_CHECKING:
    from models.enseignement.cours import Cours
    from models.eleve.eleve import Eleve


class PresenceEleve(PresenceEleveBase, table=True):
    __tablename__ = "presence_eleve"

    __table_args__ = (
        UniqueConstraint("id_cours", "id_eleve", "date_cours",
                         name="unique_cours_eleve_date"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la présence élève"
    )
    id_cours: int = Field(
        foreign_key="cours.id",
        description="Id du cours",
    )
    id_eleve: int = Field(
        foreign_key="eleve.id",
        description="Id de l'élève",
    )

    cours: "Cours" = Relationship(back_populates="presences_eleves")
    eleve: "Eleve" = Relationship(back_populates="presences")
