from sqlmodel import Session

from models.evaluations.depends_evaluation import DependsEvaluation
from repositories.base_repository import BaseRepository


class DependsEvaluationRepository(BaseRepository[DependsEvaluation]):

    def __init__(self, session: Session):
        super().__init__(DependsEvaluation, session)
