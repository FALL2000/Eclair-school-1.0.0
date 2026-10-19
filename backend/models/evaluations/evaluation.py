from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.evaluations.evaluation_dto import EvaluationBase

if TYPE_CHECKING:
    from models.administration.trimestre import Trimestre
    from models.evaluations.notation import Notation
    from models.evaluations.discipline_eleve import DisciplineEleve
    from models.evaluations.depends_evaluation import DependsEvaluation


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
    dependances: list["DependsEvaluation"] = Relationship(
        back_populates="evaluation",
        sa_relationship_kwargs={
            "foreign_keys": "DependsEvaluation.id_evaluation",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    dependants: list["DependsEvaluation"] = Relationship(
        back_populates="dependance",
        sa_relationship_kwargs={
            "foreign_keys": "DependsEvaluation.id_dependance",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
