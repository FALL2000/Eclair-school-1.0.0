from datetime import date

from sqlalchemy import or_
from sqlmodel import Session, func, select

from common.enumeration import StatutReglement
from models.administration.user import User
from models.enseignants.enseignant import Enseignant
from models.enseignants.versement_salaire import VersementSalaire
from models.enseignement.cours import Cours
from models.enseignement.presence_enseignant import PresenceEnseignant
from repositories.base_repository import BaseRepository
from repositories.enseignants.enseignant_repository import EnseignantRepository


class VersementSalaireRepository(BaseRepository[VersementSalaire]):

    def __init__(self, session: Session):
        super().__init__(VersementSalaire, session)

    def totaux_verses(self, mois: int, annee_civile: int) -> dict[int, float]:
        """Montant deja verse (versements valides) par enseignant pour un mois"""
        statement = (
            select(VersementSalaire.id_enseignant, func.sum(VersementSalaire.montant))
            .where(
                VersementSalaire.mois == mois,
                VersementSalaire.annee_civile == annee_civile,
                VersementSalaire.statut == StatutReglement.VALIDE,
            )
            .group_by(VersementSalaire.id_enseignant)
        )
        return {id_enseignant: float(total or 0) for id_enseignant, total in self.session.exec(statement).all()}

    def versements(self, id_enseignant: int, mois: int, annee_civile: int) -> list[VersementSalaire]:
        statement = (
            select(VersementSalaire)
            .where(
                VersementSalaire.id_enseignant == id_enseignant,
                VersementSalaire.mois == mois,
                VersementSalaire.annee_civile == annee_civile,
            )
            .order_by(VersementSalaire.date_versement, VersementSalaire.id)
        )
        return self.session.exec(statement).all()

    def seances_payees(self, debut: date, fin: date, id_annee: int, inclure_justifiees: bool, ids_enseignants: list[int]):
        """Seances du mois a payer : presences (et absences justifiees si la configuration le prevoit).
        Retourne des tuples (id_enseignant, heure_deb, heure_fin)"""
        if not ids_enseignants:
            return []
        condition = PresenceEnseignant.is_present == True
        if inclure_justifiees:
            condition = or_(condition, PresenceEnseignant.is_justifie == True)
        statement = (
            select(PresenceEnseignant.id_enseignant, Cours.heure_deb, Cours.heure_fin)
            .join(Cours, Cours.id == PresenceEnseignant.id_cours)
            .where(
                PresenceEnseignant.id_enseignant.in_(ids_enseignants),
                PresenceEnseignant.date_cours >= debut,
                PresenceEnseignant.date_cours <= fin,
                Cours.id_annee == id_annee,
                condition,
            )
        )
        return self.session.exec(statement).all()

    def _statement_versements(self, id_annee: int, mois: int | None, annee_civile: int | None,
                              termes: list[str], id_matiere: int | None):
        statement = (
            select(VersementSalaire, Enseignant.nom, Enseignant.prenom, User.username)
            .join(Enseignant, Enseignant.id == VersementSalaire.id_enseignant)
            .outerjoin(User, User.id == VersementSalaire.id_user)
            .where(VersementSalaire.id_annee == id_annee, *EnseignantRepository._filtres_recherche(termes, id_matiere))
        )
        if mois is not None:
            statement = statement.where(VersementSalaire.mois == mois)
        if annee_civile is not None:
            statement = statement.where(VersementSalaire.annee_civile == annee_civile)
        return statement

    def count_versements(self, id_annee, mois, annee_civile, termes, id_matiere) -> tuple[int, float]:
        """(nombre de versements, somme des versements valides) correspondant aux filtres"""
        sous_requete = self._statement_versements(id_annee, mois, annee_civile, termes, id_matiere).subquery()
        nombre = self.session.exec(select(func.count()).select_from(sous_requete)).one()
        total = self.session.exec(
            select(func.coalesce(func.sum(sous_requete.c.montant), 0))
            .where(sous_requete.c.statut == StatutReglement.VALIDE)
        ).one()
        return nombre, float(total or 0)

    def find_versements(self, id_annee, mois, annee_civile, termes, id_matiere, offset: int, limit: int):
        """Versements de l'annee scolaire, du plus recent au plus ancien.
        Retourne (versement, nom, prenom, username)"""
        statement = (
            self._statement_versements(id_annee, mois, annee_civile, termes, id_matiere)
            .order_by(VersementSalaire.date_versement.desc(), VersementSalaire.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()
