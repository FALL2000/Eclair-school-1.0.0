from datetime import date, time

from sqlmodel import Session, select

from models.enseignement.cours import Cours
from models.enseignement.presence_eleve import PresenceEleve
from repositories.base_repository import BaseRepository


class PresenceEleveRepository(BaseRepository[PresenceEleve]):

    def __init__(self, session: Session):
        super().__init__(PresenceEleve, session)

    def find_absences(
        self,
        id_classe: int,
        id_annee: int,
        date_deb: date,
        date_fin: date,
        id_eleve: int | None = None,
    ) -> list[tuple[int, bool, time, time]]:
        """Récupère les absences des élèves d'une classe sur une période,
        avec les heures de début et de fin du cours correspondant.
        Retourne des tuples (id_eleve, is_justifie, heure_deb, heure_fin)."""
        statement = (
            select(
                PresenceEleve.id_eleve,
                PresenceEleve.is_justifie,
                Cours.heure_deb,
                Cours.heure_fin,
            )
            .join(Cours, Cours.id == PresenceEleve.id_cours)
            .where(
                PresenceEleve.is_present == False,
                PresenceEleve.date_cours >= date_deb,
                PresenceEleve.date_cours <= date_fin,
                Cours.id_classe == id_classe,
                Cours.id_annee == id_annee,
            )
        )
        if id_eleve is not None:
            statement = statement.where(PresenceEleve.id_eleve == id_eleve)
        return self.session.exec(statement).all()
