from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship

from schemas.administration.niveau_dto import NiveauBase

if TYPE_CHECKING:
    from models.administration.cycle import Cycle
    from models.administration.classe import Classe
    from models.administration.serie import Serie
    from models.administration.matiere_evalue import MatiereEvalue
    from models.scolarite.tranche_pension import TranchePension


class Niveau(NiveauBase, table=True):
    __tablename__ = "niveau"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du niveau")
    id_cycle: int = Field(
        sa_column=Column(Integer, ForeignKey("cycle.id", ondelete="CASCADE")),
        description="Id du cycle"
    )
    id_serie: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "serie.id", ondelete="SET NULL"), nullable=True),
        description="Id de la serie"
    )

    cycle: "Cycle" = Relationship(back_populates="niveaux")
    serie: "Serie" = Relationship(back_populates="niveaux")
    classes: list["Classe"] = Relationship(
        back_populates="niveau", sa_relationship_kwargs={"cascade": "all, delete"})
    tranches_pension: list["TranchePension"] = Relationship(
        back_populates="niveau")
    matieres_evaluees: list["MatiereEvalue"] = Relationship(
        back_populates="niveau", sa_relationship_kwargs={"cascade": "all, delete"})
