from datetime import date

from sqlalchemy import and_
from sqlmodel import Session, select, func

from common.enumeration import StatutReglement
from models.administration.classe import Classe
from models.administration.user import User
from models.eleve.eleve import Eleve
from models.inscription.inscription import Inscription
from models.scolarite.reglement import Reglement
from models.scolarite.tranche_pension import TranchePension
from repositories.base_repository import BaseRepository
from repositories.eleve.eleve_repository import EleveRepository


class ReglementRepository(BaseRepository[Reglement]):

    def __init__(self, session: Session):
        super().__init__(Reglement, session)

    def find_all_ordered_desc(self, limit: int | None = None, offset: int | None = None) -> list[Reglement]:
        statement = select(Reglement).order_by(Reglement.date_reglement.desc())
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return self.session.exec(statement).all()

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Reglement)
        return self.session.exec(statement).one()

    def _statement_historique(self, id_annee: int | None, date_debut: date | None, date_fin: date | None, termes: list[str]):
        """Règlements d'une année avec l'élève, la tranche, la classe de l'élève cette année-là et l'utilisateur"""
        statement = (
            select(Reglement, Eleve, TranchePension.libelle, Classe.id, Classe.libelle, User.username)
            .options(*self._noload_options())
            .join(Eleve, Eleve.id == Reglement.id_eleve)
            .join(TranchePension, TranchePension.id == Reglement.id_tranche_pension)
            .outerjoin(Inscription, and_(
                Inscription.id_eleve == Reglement.id_eleve,
                Inscription.id_annee == Reglement.id_annee,
                Inscription.is_inscris == True,
            ))
            .outerjoin(Classe, Classe.id == Inscription.id_classe)
            .outerjoin(User, User.id == Reglement.id_user)
        )
        if id_annee is not None:
            statement = statement.where(Reglement.id_annee == id_annee)
        if date_debut:
            statement = statement.where(Reglement.date_reglement >= date_debut)
        if date_fin:
            statement = statement.where(Reglement.date_reglement <= date_fin)
        if termes:
            statement = statement.where(EleveRepository._filtre_termes(termes))
        return statement

    def count_historique(self, id_annee: int, date_debut: date | None, date_fin: date | None, termes: list[str]) -> tuple[int, float]:
        """(nombre de règlements, somme des règlements valides) correspondant aux filtres"""
        sous_requete = self._statement_historique(id_annee, date_debut, date_fin, termes).subquery()
        nombre = self.session.exec(select(func.count()).select_from(sous_requete)).one()
        total = self.session.exec(
            select(func.coalesce(func.sum(sous_requete.c.montant), 0))
            .where(sous_requete.c.statut == StatutReglement.VALIDE)
        ).one()
        return nombre, float(total or 0)

    def find_historique(self, id_annee: int, date_debut: date | None, date_fin: date | None, termes: list[str],
                        offset: int, limit: int):
        """Règlements du plus récent au plus ancien.
        Retourne (reglement, eleve, libellé tranche, id classe, libellé classe, username)"""
        statement = (
            self._statement_historique(id_annee, date_debut, date_fin, termes)
            .order_by(Reglement.date_reglement.desc(), Reglement.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def find_ligne_recu(self, reglement_id: int):
        """(reglement, eleve, libellé tranche, id classe, libellé classe, username) d'un règlement"""
        statement = self._statement_historique(None, None, None, []).where(Reglement.id == reglement_id)
        return self.session.exec(statement).first()

    def cumul_tranche(self, reglement: Reglement) -> float:
        """Total des règlements valides de l'élève pour la tranche et l'année, jusqu'à ce règlement inclus
        (situation au moment du règlement : un duplicata imprimé plus tard reste identique)"""
        statement = select(func.coalesce(func.sum(Reglement.montant), 0)).where(
            Reglement.id_eleve == reglement.id_eleve,
            Reglement.id_tranche_pension == reglement.id_tranche_pension,
            Reglement.id_annee == reglement.id_annee,
            Reglement.statut == StatutReglement.VALIDE,
            (Reglement.date_reglement < reglement.date_reglement)
            | ((Reglement.date_reglement == reglement.date_reglement) & (Reglement.id <= reglement.id)),
        )
        return float(self.session.exec(statement).one() or 0)
