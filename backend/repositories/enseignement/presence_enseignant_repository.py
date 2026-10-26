from datetime import date

from sqlalchemy import or_
from sqlmodel import Session, func, select

from models.administration.classe import Classe
from models.administration.matiere import Matiere
from models.enseignants.enseignant import Enseignant
from models.enseignement.cours import Cours
from models.enseignement.presence_enseignant import PresenceEnseignant
from repositories.base_repository import BaseRepository


class PresenceEnseignantRepository(BaseRepository[PresenceEnseignant]):

    def __init__(self, session: Session):
        super().__init__(PresenceEnseignant, session)

    def get_cours(self, id_cours: int) -> Cours | None:
        return self.session.get(Cours, id_cours)

    def find_presence(self, id_cours: int, date_cours: date, exclude_id: int | None = None) -> PresenceEnseignant | None:
        statement = select(PresenceEnseignant).where(
            PresenceEnseignant.id_cours == id_cours, PresenceEnseignant.date_cours == date_cours)
        if exclude_id is not None:
            statement = statement.where(PresenceEnseignant.id != exclude_id)
        return self.session.exec(statement).first()

    def cours_du_jour(self, jour: str, id_annee: int, termes: list[str], id_enseignant: int | None,
                      id_classe: int | None = None):
        """Cours planifies ce jour de la semaine (toutes classes) dans l'annee, tries par heure puis classe.
        Retourne (cours, classe, matiere, nom, prenom)"""
        statement = (
            select(Cours, Classe.libelle, Matiere.libelle, Enseignant.nom, Enseignant.prenom)
            .join(Classe, Classe.id == Cours.id_classe)
            .join(Matiere, Matiere.id == Cours.id_matiere)
            .join(Enseignant, Enseignant.id == Cours.id_enseignant)
            .where(Cours.id_annee == id_annee, func.lower(Cours.jour) == jour.lower())
        )
        for terme in termes:
            statement = statement.where(or_(
                func.lower(Enseignant.nom).contains(terme.lower(), autoescape=True),
                func.lower(Enseignant.prenom).contains(terme.lower(), autoescape=True),
            ))
        if id_enseignant is not None:
            statement = statement.where(Cours.id_enseignant == id_enseignant)
        if id_classe is not None:
            statement = statement.where(Cours.id_classe == id_classe)
        return self.session.exec(statement.order_by(Cours.heure_deb, Classe.libelle)).all()

    def presences_du_jour(self, date_cours: date, ids_cours: list[int]) -> dict[int, PresenceEnseignant]:
        if not ids_cours:
            return {}
        statement = select(PresenceEnseignant).where(
            PresenceEnseignant.date_cours == date_cours, PresenceEnseignant.id_cours.in_(ids_cours))
        return {p.id_cours: p for p in self.session.exec(statement).all()}
