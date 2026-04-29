from fastapi import HTTPException

from schemas.administration.niveau_dto import NiveauCreateDTO, NiveauUpdateDTO
from models.administration.niveau import Niveau
from repositories.administration.niveau_repository import NiveauRepository
from repositories.administration.annee_repository import AnneeRepository


class NiveauService:
    def __init__(self, niveau_repository: NiveauRepository, annee_repository: AnneeRepository):
        self.niveau_repository = niveau_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_niveau = self.niveau_repository.findByCode(code)
        if len(exist_niveau) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"Le niveau avec le code {code} existe déjà."
                }
            )

    def _check_niveau_exists(self, db_niveau: Niveau | None):
        if db_niveau is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "NIVEAU_NOT_FOUND",
                    "message": "niveau non trouvé"
                }
            )

    def add_niveau(self, niveau_in: NiveauCreateDTO, cycle_id: int, serie_id: int):
        """Ajoute un niveau en BD"""
        try:
            self._check_code_exists(niveau_in.code)
            db_niveau = Niveau.model_validate(niveau_in)
            db_niveau.id_cycle = cycle_id
            db_niveau.id_serie = serie_id
            new_niveau = self.niveau_repository.save(db_niveau)
            self.niveau_repository.session.commit()
            return new_niveau
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.niveau_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du niveau: {str(e)}")

    def update_niveau(self, niveau_update: NiveauUpdateDTO, niveau_id: int):
        """Modifie un niveau BD"""
        try:
            db_niveau = self.niveau_repository.findOne(niveau_id)
            self._check_niveau_exists(db_niveau)
            if niveau_update.code is not None and niveau_update.code != db_niveau.code:
                self._check_code_exists(niveau_update.code)
            update_data = niveau_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_niveau, key, value)
            new_niveau = self.niveau_repository.save(db_niveau)
            self.niveau_repository.session.commit()
            return new_niveau
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.niveau_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du niveau: {str(e)}")

    def delete_niveau(self, niveau_id: int):
        """Supprime un niveau en BD"""
        try:
            db_niveau = self.niveau_repository.findOne(niveau_id)
            self._check_niveau_exists(db_niveau)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un niveau durant une annee scolaire en cours"
                    }
                )
            delete_niveau = self.niveau_repository.deleteOne(niveau_id)
            if delete_niveau:
                return {
                    "success": True,
                    "detail": {"id": niveau_id, "message": "Niveau supprimé"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": niveau_id, "message": "Niveau non supprimé"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.niveau_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du niveau: {str(e)}")

    def get_one_niveau(self, niveau_id: int):
        """Recupere un niveau en BD"""
        try:
            db_niveau = self.niveau_repository.findOne(niveau_id)
            self._check_niveau_exists(db_niveau)
            return db_niveau
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.niveau_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du niveau: {str(e)}")

    def get_all_niveau(self):
        """Recupere tous les niveaux en BD"""
        try:
            db_niveaux = self.niveau_repository.findAll()
            return db_niveaux
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.niveau_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des niveaux: {str(e)}")
