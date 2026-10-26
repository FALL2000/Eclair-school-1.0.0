from datetime import date
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field

from common.enumeration import StatutReglement
from schemas.enseignants.salaire_dto import VersementSalaireBase


class VersementSalaire(VersementSalaireBase, table=True):
    """Versement (total ou partiel) du salaire d'un enseignant pour un mois"""
    __tablename__ = "versement_salaire"

    id: Optional[int] = Field(default=None, primary_key=True, description="Id du versement")
    id_enseignant: int = Field(foreign_key="enseignant.id", description="Id de l'enseignant")
    id_annee: int = Field(foreign_key="annee.id", description="Annee scolaire")
    date_versement: date = Field(description="Date du versement", nullable=False)
    montant_du: float = Field(description="Salaire du mois au moment du versement", nullable=False)
    nb_heures: Optional[float] = Field(default=None, nullable=True, description="Heures payees (salaire horaire)")
    statut: StatutReglement = Field(
        default=StatutReglement.VALIDE, nullable=False, description="Statut du versement (valide, annule)")
    id_user: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        description="Utilisateur ayant enregistre le versement",
    )
