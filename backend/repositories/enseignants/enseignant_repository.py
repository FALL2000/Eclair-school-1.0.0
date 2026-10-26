from sqlalchemy import and_, exists, func, or_
from sqlmodel import Session, select

from models.enseignants.enseignant import Enseignant
from models.enseignement.enseignement import Enseignement
from repositories.base_repository import BaseRepository


class EnseignantRepository(BaseRepository[Enseignant]):

    def __init__(self, session: Session):
        super().__init__(Enseignant, session)

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Enseignant)
        return self.session.exec(statement).one()

    @staticmethod
    def _filtres_recherche(termes: list[str], id_matiere: int | None) -> list:
        """Chaque mot doit apparaitre dans le nom ou le prenom (insensible a la casse) ;
        id_matiere : l'enseignant doit enseigner cette matiere"""
        filtres = [
            or_(
                func.lower(Enseignant.nom).contains(terme.lower(), autoescape=True),
                func.lower(Enseignant.prenom).contains(terme.lower(), autoescape=True),
            )
            for terme in termes
        ]
        if id_matiere is not None:
            filtres.append(exists().where(and_(
                Enseignement.id_enseignant == Enseignant.id,
                Enseignement.id_matiere == id_matiere,
            )))
        return filtres

    def find_pour_salaire(self, termes: list[str], id_matiere: int | None = None) -> list[Enseignant]:
        """Enseignants actifs et inactifs filtres par nom ou prenom et matiere enseignee, tries par nom"""
        statement = (
            select(Enseignant)
            .where(*self._filtres_recherche(termes, id_matiere))
            .order_by(Enseignant.nom, Enseignant.prenom)
        )
        return self.session.exec(statement).all()

    @staticmethod
    def _filtres_moyen_paiement(termes: list[str], id_matiere: int | None, configure: bool | None) -> list:
        filtres = [Enseignant.is_active == True, *EnseignantRepository._filtres_recherche(termes, id_matiere)]
        if configure is True:
            filtres.append(Enseignant.moyen_paiement.is_not(None))
        elif configure is False:
            filtres.append(Enseignant.moyen_paiement.is_(None))
        return filtres

    def count_moyens_paiement(self, termes: list[str], id_matiere: int | None, configure: bool | None) -> int:
        statement = select(func.count()).select_from(Enseignant).where(
            *self._filtres_moyen_paiement(termes, id_matiere, configure))
        return self.session.exec(statement).one()

    def find_moyens_paiement(self, termes: list[str], id_matiere: int | None, configure: bool | None,
                             offset: int, limit: int) -> list[Enseignant]:
        """Enseignants actifs filtres (configure : moyen de paiement renseigne ou non), tries par nom"""
        statement = (
            select(Enseignant)
            .where(*self._filtres_moyen_paiement(termes, id_matiere, configure))
            .order_by(Enseignant.nom, Enseignant.prenom)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def count_search(self, termes: list[str], id_matiere: int | None) -> int:
        statement = select(func.count()).select_from(Enseignant).where(*self._filtres_recherche(termes, id_matiere))
        return self.session.exec(statement).one()

    def search(self, termes: list[str], id_matiere: int | None, offset: int, limit: int) -> list[Enseignant]:
        """Enseignants filtres, tries par nom puis prenom (les enseignements se chargent a la lecture)"""
        statement = (
            select(Enseignant)
            .where(*self._filtres_recherche(termes, id_matiere))
            .order_by(Enseignant.nom, Enseignant.prenom)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()
