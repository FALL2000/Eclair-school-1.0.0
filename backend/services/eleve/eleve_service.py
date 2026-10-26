from fastapi import HTTPException

from models.eleve.eleve import Eleve
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.eleve.eleve_repository import EleveRepository
from schemas.eleve.eleve_dto import EleveUpdateDTO, PaginatedEleveClasse
from services.administration.annee_service import AnneeService

NB_CARACTERES_MIN_RECHERCHE = 3


class EleveService:
    def __init__(
        self,
        eleve_repository: EleveRepository,
        annee_repository: AnneeRepository,
        classe_repository: ClasseRepository,
    ):
        self.eleve_repository = eleve_repository
        self.annee_repository = annee_repository
        self.classe_repository = classe_repository

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    @staticmethod
    def _termes(q: str | None) -> list[str]:
        """Découpe la recherche en mots (ex : « ngono marie » -> ["ngono", "marie"])"""
        return [terme for terme in (q or "").split() if terme]

    def _check_eleve_exists(self, db_eleve: Eleve | None):
        if db_eleve is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ELEVE_NOT_FOUND",
                    "message": "Eleve non trouve"
                }
            )

    def update_eleve(self, eleve_update: EleveUpdateDTO, eleve_id: int):
        try:
            db_eleve = self.eleve_repository.findOne(eleve_id)
            self._check_eleve_exists(db_eleve)
            update_data = eleve_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_eleve, key, value)
            new_eleve = self.eleve_repository.save(db_eleve)
            self.eleve_repository.session.commit()
            return new_eleve
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.eleve_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'eleve: {str(e)}")

    def get_one_eleve(self, eleve_id: int):
        try:
            db_eleve = self.eleve_repository.findOne(eleve_id)
            self._check_eleve_exists(db_eleve)
            return db_eleve
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.eleve_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de l'eleve: {str(e)}")

    def get_all_eleve(self):
        try:
            return self.eleve_repository.findAll()
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.eleve_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des eleves: {str(e)}")

    def search_eleves(self, q: str, limit: int):
        """Recherche des élèves dans toute l'école par nom, prénom ou matricule.
        Chaque mot doit apparaître dans l'un de ces champs. Retourne aussi la classe de l'année en cours."""
        try:
            if len(q.strip()) < NB_CARACTERES_MIN_RECHERCHE:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "RECHERCHE_TROP_COURTE",
                        "message": f"Saisissez au moins {NB_CARACTERES_MIN_RECHERCHE} caractères",
                    },
                )
            annee = self._get_annee_service().get_annee_scolaire()[0]
            resultats = self.eleve_repository.search(self._termes(q), annee.id, limit)
            return [
                {
                    **eleve.model_dump(),
                    "id_classe": classe.id if classe is not None else None,
                    "classe": classe.libelle if classe is not None else None,
                }
                for eleve, classe in resultats
            ]
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recherche des eleves: {str(e)}")

    def get_eleves_by_classe(
        self, id_classe: int, page: int | None, page_size: int | None,
        q: str | None = None, genre: str | None = None,
    ) -> PaginatedEleveClasse:
        """Élèves inscrits dans une classe pour l'année en cours, paginés et triés par nom.
        Filtres optionnels : q (nom, prénom ou matricule) et genre."""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            if self.classe_repository.findOne(id_classe) is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "CLASSE_NOT_FOUND", "message": "Classe non trouvee"},
                )
            termes = self._termes(q)
            total_items = self.eleve_repository.count_by_classe(id_classe, annee.id, termes, genre)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            lignes = self.eleve_repository.find_by_classe(
                id_classe, annee.id, termes, genre, offset=(page - 1) * page_size, limit=page_size)
            return PaginatedEleveClasse(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                eleves=[
                    {
                        **eleve.model_dump(),
                        "id_inscription": inscription.id,
                        "is_redoublant": inscription.is_redoublant,
                        "is_nouveau": inscription.is_nouveau,
                        "date_inscris": inscription.date_inscris,
                    }
                    for eleve, inscription in lignes
                ],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des eleves de la classe: {str(e)}")
