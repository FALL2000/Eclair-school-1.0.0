from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.evaluations.evaluation_dto import EvaluationBase

if TYPE_CHECKING:
    from models.administration.trimestre import Trimestre
    from models.evaluations.notation import Notation
    from models.evaluations.discipline_eleve import DisciplineEleve


class Evaluation(EvaluationBase, table=True):
    __tablename__ = "evaluation"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'évaluation"
    )
    id_trimestre: int = Field(
        foreign_key="trimestre.id",
        description="Id du trimestre",
    )

    trimestre: "Trimestre" = Relationship(back_populates="evaluations")
    notations: list["Notation"] = Relationship(back_populates="evaluation")
    disciplines: list["DisciplineEleve"] = Relationship(
        back_populates="evaluation"
    )
