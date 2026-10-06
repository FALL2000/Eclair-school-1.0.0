from sqlmodel import Session

from models.evaluations.evaluation import Evaluation
from repositories.base_repository import BaseRepository


class EvaluationRepository(BaseRepository[Evaluation]):

    def __init__(self, session: Session):
        super().__init__(Evaluation, session)
