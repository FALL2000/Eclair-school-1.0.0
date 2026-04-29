from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.inscription.inscription_dto import InscriptionBase

if TYPE_CHECKING:
    from models.administration.annee import Annee
    from models.administration.classe import Classe
    from models.administration.user import User
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
    date_inscris: Optional[date] = Field(
        default=None,
        nullable=True,
        description="Date d'inscription de l'eleve",
    )
    is_inscris: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'inscription est finalisee",
    )
    id_user: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("user.id", ondelete="SET NULL"),
            nullable=True,
        ),
        description="Utilisateur associe a l'inscription",
    )

    eleve: "Eleve" = Relationship(
        back_populates="inscriptions", sa_relationship_kwargs={"lazy": "joined"})
    classe: "Classe" = Relationship(back_populates="inscriptions")
    annee: "Annee" = Relationship(back_populates="inscriptions")
    user: Optional["User"] = Relationship(back_populates="inscriptions")
