from typing import Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.evaluations.depends_evaluation_dto import DependsEvaluationBase

if TYPE_CHECKING:
    from models.evaluations.evaluation import Evaluation


class DependsEvaluation(DependsEvaluationBase, table=True):
    __tablename__ = "depends_evaluation"

    __table_args__ = (
        UniqueConstraint(
            "id_evaluation", "id_dependance",
            name="unique_evaluation_dependance"
        ),
        CheckConstraint(
            "id_evaluation <> id_dependance",
            name="check_evaluation_differente_dependance"
        ),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la dépendance d'évaluation"
    )
    id_evaluation: int = Field(
        sa_column=Column(Integer, ForeignKey("evaluation.id", ondelete="CASCADE"), nullable=False),
        description="Id de l'évaluation regroupant les dépendances",
    )
    id_dependance: int = Field(
        sa_column=Column(Integer, ForeignKey("evaluation.id", ondelete="CASCADE"), nullable=False),
        description="Id de l'évaluation dont dépend l'évaluation",
    )

    evaluation: "Evaluation" = Relationship(
        back_populates="dependances",
        sa_relationship_kwargs={"foreign_keys": "DependsEvaluation.id_evaluation"},
    )
    dependance: "Evaluation" = Relationship(
        back_populates="dependants",
        sa_relationship_kwargs={"foreign_keys": "DependsEvaluation.id_dependance"},
    )
