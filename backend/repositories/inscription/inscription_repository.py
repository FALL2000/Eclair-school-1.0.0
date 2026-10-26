from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from common.enumeration import StatutReglement
from models.administration.classe import Classe
from models.administration.niveau import Niveau
from models.administration.user import User
from models.eleve.eleve import Eleve
from models.enseignement.cours import Cours
from models.enseignement.presence_eleve import PresenceEleve
from models.evaluations.discipline_eleve import DisciplineEleve
from models.evaluations.notation import Notation
from models.inscription.inscription import Inscription
from models.scolarite.reglement import Reglement
from repositories.base_repository import BaseRepository
from repositories.eleve.eleve_repository import EleveRepository


class InscriptionRepository(BaseRepository[Inscription]):

    def __init__(self, session: Session):
        super().__init__(Inscription, session)

    def _statement_historique(self, date_debut: date | None, date_fin: date | None, termes: list[str]):
        user_inscription = aliased(User)
        user_modification = aliased(User)
        statement = (
            select(Inscription, Eleve, Classe, Niveau, user_inscription.username, user_modification.username)
            .options(*self._noload_options())
            .join(Eleve, Eleve.id == Inscription.id_eleve)
            .join(Classe, Classe.id == Inscription.id_classe)
            .join(Niveau, Niveau.id == Classe.id_niveau)
            .outerjoin(user_inscription, user_inscription.id == Inscription.id_user)
            .outerjoin(user_modification, user_modification.id == Inscription.id_user_modification)
            .where(Inscription.is_inscris == True)
        )
        if date_debut:
            statement = statement.where(Inscription.date_inscris >= date_debut)
        if date_fin:
            statement = statement.where(Inscription.date_inscris <= date_fin)
        if termes:
            statement = statement.where(EleveRepository._filtre_termes(termes))
        return statement

    def count_historique(self, date_debut: date | None, date_fin: date | None, termes: list[str]) -> int:
        sous_requete = self._statement_historique(date_debut, date_fin, termes).subquery()
        return self.session.exec(select(func.count()).select_from(sous_requete)).one()

    def find_historique(self, date_debut: date | None, date_fin: date | None, termes: list[str], offset: int, limit: int):
        """Inscriptions finalisees, de la plus recente a la plus ancienne.
        Retourne (inscription, eleve, classe, niveau, username inscription, username derniere modification)"""
        statement = (
            self._statement_historique(date_debut, date_fin, termes)
            .order_by(Inscription.date_inscris.desc(), Inscription.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def find_ligne_historique(self, inscription_id: int):
        statement = self._statement_historique(None, None, []).where(Inscription.id == inscription_id)
        return self.session.exec(statement).first()

    def donnees_eleve_annee(self, id_eleve: int, id_annee: int) -> list[str]:
        """Types de donnees deja enregistrees pour un eleve pendant une annee (notes, discipline, appel)"""
        donnees = []
        if self.session.exec(select(func.count()).select_from(Notation).where(
                Notation.id_eleve == id_eleve, Notation.id_annee == id_annee)).one():
            donnees.append("notes")
        if self.session.exec(select(func.count()).select_from(DisciplineEleve).where(
                DisciplineEleve.id_eleve == id_eleve, DisciplineEleve.id_annee == id_annee)).one():
            donnees.append("discipline")
        if self.session.exec(select(func.count()).select_from(PresenceEleve).join(Cours, Cours.id == PresenceEleve.id_cours).where(
                PresenceEleve.id_eleve == id_eleve, Cours.id_annee == id_annee)).one():
            donnees.append("appel")
        return donnees

    def has_reglements_annee(self, id_eleve: int, id_annee: int) -> bool:
        """Reglements valides de l'eleve pendant l'annee (ils portent sur les tranches de son niveau)"""
        return self.session.exec(select(func.count()).select_from(Reglement).where(
            Reglement.id_eleve == id_eleve, Reglement.id_annee == id_annee,
            Reglement.statut == StatutReglement.VALIDE)).one() > 0
