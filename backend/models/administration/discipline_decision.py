from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.discipline_decision_dto import DisciplineDecisionBase

if TYPE_CHECKING:
    from models.evaluations.discipline_eleve import DisciplineEleve


class DisciplineDecision(DisciplineDecisionBase, table=True):
    __tablename__ = "discipline_decision"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la décision disciplinaire"
    )

    disciplines_eleves: list["DisciplineEleve"] = Relationship(
        back_populates="discipline_decision")
