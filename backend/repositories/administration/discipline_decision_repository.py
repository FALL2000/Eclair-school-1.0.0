from sqlmodel import Session, select

from models.administration.discipline_decision import DisciplineDecision
from repositories.base_repository import BaseRepository


class DisciplineDecisionRepository(BaseRepository[DisciplineDecision]):

    def __init__(self, session: Session):
        super().__init__(DisciplineDecision, session)

    def find_chevauchement(self, nb_heure_min: int, nb_heure_max: int) -> list[DisciplineDecision]:
        """Récupère les décisions dont l'intervalle [nb_heure_min, nb_heure_max] chevauche celui donné"""
        statement = select(DisciplineDecision).where(
            DisciplineDecision.nb_heure_min <= nb_heure_max,
            DisciplineDecision.nb_heure_max >= nb_heure_min,
        )
        return self.session.exec(statement).all()
