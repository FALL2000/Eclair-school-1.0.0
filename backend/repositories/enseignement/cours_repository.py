from datetime import time

from sqlmodel import Session, select

from models.enseignement.cours import Cours
from repositories.base_repository import BaseRepository


class CoursRepository(BaseRepository[Cours]):

    def __init__(self, session: Session):
        super().__init__(Cours, session)

    def find_chevauchement(
        self,
        jour: str,
        heure_deb: time,
        heure_fin: time,
        id_annee: int,
        id_classe: int | None = None,
        id_enseignant: int | None = None,
    ) -> list[Cours]:
        """Récupère les cours dont le créneau chevauche [heure_deb, heure_fin[ le même jour.
        Deux créneaux se chevauchent si existant.heure_deb < heure_fin ET existant.heure_fin > heure_deb."""
        statement = (
            select(Cours)
            .options(*self._noload_options())
            .where(
                Cours.jour == jour,
                Cours.id_annee == id_annee,
                Cours.heure_deb < heure_fin,
                Cours.heure_fin > heure_deb,
            )
        )
        if id_classe is not None:
            statement = statement.where(Cours.id_classe == id_classe)
        if id_enseignant is not None:
            statement = statement.where(Cours.id_enseignant == id_enseignant)
        return self.session.exec(statement).all()
