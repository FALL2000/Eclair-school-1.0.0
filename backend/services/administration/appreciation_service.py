from fastapi import HTTPException

from schemas.administration.appreciation_dto import AppreciationCreateDTO, AppreciationUpdateDTO
from repositories.administration.appreciation_repository import AppreciationRepository
from models.administration.appreciation import Appreciation


class AppreciationService:
    def __init__(self, appreciation_repository: AppreciationRepository):
        self.appreciation_repository = appreciation_repository

    def _check_libelle_exists(self, libelle: str):
        exist_appreciation = self.appreciation_repository.findByLibelle(
            libelle)
        if len(exist_appreciation) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L' appreciation avec le libelle {libelle} existe déjà."
                }
            )

    def _check_appreciation_exists(self, db_appreciation: Appreciation | None):
        if db_appreciation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "APPRECIATION_NOT_FOUND",
                    "message": "appreciation non trouvé"
                }
            )

    def add_appreciation(self, appreciation_in: AppreciationCreateDTO):
        """Ajoute une appreciation en BD"""
        try:
            self._check_libelle_exists(appreciation_in.libelle)
            db_appreciation = Appreciation.model_validate(appreciation_in)
            new_appreciation = self.appreciation_repository.save(
                db_appreciation)
            self.appreciation_repository.session.commit()
            return new_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de l'appreciation: {str(e)}")

    def update_appreciation(self, appreciation_update: AppreciationUpdateDTO, appreciation_id: int):
        """Modifie une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            if appreciation_update.libelle is not None and appreciation_update.libelle != db_appreciation.libelle:
                self._check_libelle_exists(appreciation_update.libelle)
            update_data = appreciation_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_appreciation, key, value)
            new_appreciation = self.appreciation_repository.save(
                db_appreciation)
            self.appreciation_repository.session.commit()
            return new_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'appreciation: {str(e)}")

    def delete_appreciation(self, appreciation_id: int):
        """Supprime une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            delete_appreciation = self.appreciation_repository.deleteOne(
                appreciation_id)
            if delete_appreciation:
                return {
                    "success": True,
                    "detail": {"id": appreciation_id, "message": "appreciation supprimée"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": appreciation_id, "message": "appreciation non supprimée"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'appreciation: {str(e)}")

    def get_one_appreciation(self, appreciation_id: int):
        """Récupère une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            return db_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de l'appreciation: {str(e)}")

    def get_all_appreciation(self):
        """Récupère toutes les appreciations en BD"""
        try:
            db_appreciations = self.appreciation_repository.findAll()
            return db_appreciations
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des appreciations: {str(e)}")
