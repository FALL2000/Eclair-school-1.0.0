from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.appreciation_dto import AppreciationBase

if TYPE_CHECKING:
    from evaluations.notation import Notation


class Appreciation(AppreciationBase, table=True):
    __tablename__ = "appreciation"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'appréciation"
    )

    notations: list["Notation"] = Relationship(back_populates="appreciation")
