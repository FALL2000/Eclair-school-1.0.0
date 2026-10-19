from typing import List, Optional

from sqlmodel import Field, SQLModel


class DependsEvaluationBase(SQLModel):
    pourcentage: float = Field(
        gt=0,
        le=100,
        description="Pourcentage que représente l'évaluation dépendante dans la note de l'évaluation",
        nullable=False,
    )


class DependsEvaluationCreateDTO(DependsEvaluationBase):
    id_dependance: int


class DependsEvaluationBulkCreateDTO(SQLModel):
    dependances: List[DependsEvaluationCreateDTO]


class DependsEvaluationUpdateDTO(SQLModel):
    pourcentage: Optional[float] = Field(default=None, gt=0, le=100)


class DependsEvaluationResponseDTO(DependsEvaluationBase):
    id: int
    id_evaluation: int
    id_dependance: int
