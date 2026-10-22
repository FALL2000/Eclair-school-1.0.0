from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.appreciation_dto import AppreciationBase

if TYPE_CHECKING:
    from evaluations.notation import Notation
    from models.administration.bareme import Bareme


class Appreciation(AppreciationBase, table=True):
    __tablename__ = "appreciation"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'appréciation"
    )
    id_bareme: int = Field(
        foreign_key="bareme.id",
        description="Id du barème de notation auquel appartient l'appréciation",
    )

    notations: list["Notation"] = Relationship(back_populates="appreciation")
    bareme: "Bareme" = Relationship(back_populates="appreciations")
