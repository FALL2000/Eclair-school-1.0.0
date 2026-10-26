from sqlmodel import Session, func, select

from models.enseignement.cours import Cours
from models.enseignement.enseignement import Enseignement
from repositories.base_repository import BaseRepository


class EnseignementRepository(BaseRepository[Enseignement]):

    def __init__(self, session: Session):
        super().__init__(Enseignement, session)

    def count_cours_planifies(self, id_enseignant: int, id_matiere: int, ids_annees: list[int]) -> int:
        """Nombre de cours de l'emploi du temps de ces annees pour cet enseignant et cette matiere"""
        if not ids_annees:
            return 0
        statement = select(func.count()).select_from(Cours).where(
            Cours.id_enseignant == id_enseignant,
            Cours.id_matiere == id_matiere,
            Cours.id_annee.in_(ids_annees),
        )
        return self.session.exec(statement).one()
