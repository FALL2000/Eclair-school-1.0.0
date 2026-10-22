from sqlmodel import Session, select

from models.administration.appreciation import Appreciation
from repositories.base_repository import BaseRepository


class AppreciationRepository(BaseRepository[Appreciation]):

    def __init__(self, session: Session):
        super().__init__(Appreciation, session)

    def find_chevauchement(self, id_bareme: int, valeur_min: float, valeur_max: float) -> list[Appreciation]:
        """Récupère les appréciations d'un barème dont l'intervalle fermé [valeur_min, valeur_max]
        chevauche celui donné"""
        statement = select(Appreciation).where(
            Appreciation.id_bareme == id_bareme,
            Appreciation.valeur_min <= valeur_max,
            Appreciation.valeur_max >= valeur_min,
        )
        return self.session.exec(statement).all()
