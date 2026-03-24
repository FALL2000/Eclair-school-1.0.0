from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, UniqueConstraint
from schemas.scolarite.tranche_pension_dto import TranchePensionBase

if TYPE_CHECKING:
    from models.administration.niveau import Niveau
    from models.scolarite.reglement import Reglement


class TranchePension(TranchePensionBase, table=True):
    __tablename__ = "tranche_pension"

    __table_args__ = (
        UniqueConstraint("id_niveau", "numero_ordre",
                         name="unique_num_ordre_niveau"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la tranche d'une pension")
    id_niveau: int = Field(
        foreign_key="niveau.id",
        description="Id du niveau"
    )

    niveau: "Niveau" = Relationship(back_populates="tranches_pension")
    reglements: list["Reglement"] = Relationship(
        back_populates="tranche_pension")
