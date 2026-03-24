from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.trimestre_dto import TrimestreBase

if TYPE_CHECKING:
    from models.evaluations.evaluation import Evaluation


class Trimestre(TrimestreBase, table=True):
    __tablename__ = "trimestre"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du trimestre"
    )

    evaluations: list["Evaluation"] = Relationship(back_populates="trimestre")
