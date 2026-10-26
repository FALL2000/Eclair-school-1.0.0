from sqlalchemy import and_, func, or_
from sqlmodel import Session, select

from models.administration.classe import Classe
from models.eleve.eleve import Eleve
from models.inscription.inscription import Inscription
from repositories.base_repository import BaseRepository


class EleveRepository(BaseRepository[Eleve]):

    def __init__(self, session: Session):
        super().__init__(Eleve, session)

    @staticmethod
    def _filtre_termes(termes: list[str]):
        """Chaque mot recherché doit apparaître dans le nom, le prénom ou le matricule (insensible à la casse)"""
        return and_(*[
            or_(
                func.lower(Eleve.nom).contains(terme.lower(), autoescape=True),
                func.lower(Eleve.prenom).contains(terme.lower(), autoescape=True),
                func.lower(Eleve.matricule).contains(terme.lower(), autoescape=True),
            )
            for terme in termes
        ])

    def search(self, termes: list[str], id_annee: int, limit: int) -> list[tuple[Eleve, Classe | None]]:
        """Recherche des élèves actifs dans toute l'école.
        Retourne (élève, classe de l'année en cours ou None s'il n'est pas inscrit cette année)"""
        statement = (
            select(Eleve, Classe)
            .options(*self._noload_options())
            .outerjoin(Inscription, and_(
                Inscription.id_eleve == Eleve.id,
                Inscription.id_annee == id_annee,
                Inscription.is_inscris == True,
            ))
            .outerjoin(Classe, Classe.id == Inscription.id_classe)
            .where(Eleve.is_active == True, self._filtre_termes(termes))
            .order_by(Eleve.nom, Eleve.prenom)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def _statement_classe(self, id_classe: int, id_annee: int, termes: list[str], genre: str | None):
        statement = (
            select(Eleve, Inscription)
            .options(*self._noload_options())
            .join(Inscription, Inscription.id_eleve == Eleve.id)
            .where(
                Inscription.id_classe == id_classe,
                Inscription.id_annee == id_annee,
                Inscription.is_inscris == True,
            )
        )
        if termes:
            statement = statement.where(self._filtre_termes(termes))
        if genre:
            statement = statement.where(Eleve.genre == genre)
        return statement

    def count_by_classe(self, id_classe: int, id_annee: int, termes: list[str], genre: str | None) -> int:
        sous_requete = self._statement_classe(id_classe, id_annee, termes, genre).subquery()
        return self.session.exec(select(func.count()).select_from(sous_requete)).one()

    def find_by_classe(
        self, id_classe: int, id_annee: int, termes: list[str], genre: str | None,
        offset: int, limit: int,
    ) -> list[tuple[Eleve, Inscription]]:
        """Élèves inscrits dans une classe pour une année, triés par nom puis prénom"""
        statement = (
            self._statement_classe(id_classe, id_annee, termes, genre)
            .order_by(Eleve.nom, Eleve.prenom)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()
