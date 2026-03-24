from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.scolarite.reglement_dto import ReglementBase

if TYPE_CHECKING:
    from models.administration.annee import Annee
    from models.eleve.eleve import Eleve
    from models.scolarite.tranche_pension import TranchePension


class Reglement(ReglementBase, table=True):
    __tablename__ = "reglement"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du reglement")
    id_tranche_pension: int = Field(
        foreign_key="tranche_pension.id", description="Id de la tranche"
    )
    id_eleve: int = Field(
        foreign_key="eleve.id",
        description="Id de l'eleve"
    )
    id_annee: int = Field(foreign_key="annee.id", description="Id de l'annee")
    date_reglement: date = Field(
        description="date du reglement", nullable=False)

    tranche_pension: "TranchePension" = Relationship(
        back_populates="reglements")
    eleve: "Eleve" = Relationship(back_populates="reglements")
    annee: "Annee" = Relationship(back_populates="reglements")
