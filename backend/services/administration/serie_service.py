from fastapi import HTTPException

from repositories.administration.annee_repository import AnneeRepository
from models.administration.serie import Serie
from schemas.administration.serie_dto import SerieCreateDTO, SerieUpdateDTO
from repositories.administration.serie_repository import SerieRepository


class SerieService:
    def __init__(self, serie_repository: SerieRepository, annee_repository: AnneeRepository):
        self.serie_repository = serie_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_serie = self.serie_repository.findByCode(code)
        if len(exist_serie) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La série avec le code {code} existe déjà."
                }
            )

    def _check_serie_exists(self, db_serie: Serie | None):
        if db_serie is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "SERIE_NOT_FOUND",
                    "message": "Série non trouvée"
                }
            )

    def add_serie(self, serie_in: SerieCreateDTO):
        """Ajoute une série en BD"""
        try:
            self._check_code_exists(serie_in.code)
            db_serie = Serie.model_validate(serie_in)
            new_serie = self.serie_repository.save(db_serie)
            self.serie_repository.session.commit()
            return new_serie
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.serie_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la série: {str(e)}")

    def update_serie(self, serie_update: SerieUpdateDTO, serie_id: int):
        """Modifie une série BD"""
        try:
            db_serie = self.serie_repository.findOne(serie_id)
            self._check_serie_exists(db_serie)
            if serie_update.code is not None and serie_update.code != db_serie.code:
                self._check_code_exists(serie_update.code)
            update_data = serie_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_serie, key, value)
            new_serie = self.serie_repository.save(db_serie)
            self.serie_repository.session.commit()
            return new_serie
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.serie_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la série: {str(e)}")

    def delete_serie(self, serie_id: int):
        """Supprime une série en BD"""
        try:
            db_serie = self.serie_repository.findOne(serie_id)
            self._check_serie_exists(db_serie)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une série durant une année scolaire en cours"
                    }
                )
            delete_serie = self.serie_repository.deleteOne(serie_id)
            if delete_serie:
                return {
                    "success": True,
                    "detail": {"id": serie_id, "message": "Série supprimée"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": serie_id, "message": "Série non supprimée"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.serie_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la série: {str(e)}")

    def get_one_serie(self, serie_id: int):
        """Récupère une série en BD"""
        try:
            db_serie = self.serie_repository.findOne(serie_id)
            self._check_serie_exists(db_serie)
            return db_serie
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.serie_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de la série: {str(e)}")

    def get_all_serie(self):
        """Récupère toutes les séries en BD"""
        try:
            db_series = self.serie_repository.findAll()
            return db_series
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.serie_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des séries: {str(e)}")
