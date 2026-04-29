from fastapi import HTTPException

from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.trimestre_repository import TrimestreRepository
from models.administration.trimestre import Trimestre
from schemas.administration.trimestre_dto import TrimestreCreateDTO, TrimestreUpdateDTO


class TrimestreService:
    def __init__(self, trimestre_repository: TrimestreRepository, annee_repository: AnneeRepository):
        self.trimestre_repository = trimestre_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_trimestre = self.trimestre_repository.findByCode(code)
        if len(exist_trimestre) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"Le trimestre avec le code {code} existe déjà."
                }
            )

    def _check_trimestre_exists(self, db_trimestre: Trimestre | None):
        if db_trimestre is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "TRIMESTRE_NOT_FOUND",
                    "message": "Trimestre non trouvé"
                }
            )

    def add_trimestre(self, trimestre_in: TrimestreCreateDTO):
        """Ajoute un trimestre en BD"""
        try:
            self._check_code_exists(trimestre_in.code)
            db_trimestre = Trimestre.model_validate(trimestre_in)
            new_trimestre = self.trimestre_repository.save(db_trimestre)
            self.trimestre_repository.session.commit()
            return new_trimestre
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.trimestre_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du trimestre: {str(e)}")

    def update_trimestre(self, trimestre_update: TrimestreUpdateDTO, trimestre_id: int):
        """Modifie un trimestre en BD"""
        try:
            db_trimestre = self.trimestre_repository.findOne(trimestre_id)
            self._check_trimestre_exists(db_trimestre)
            if trimestre_update.code is not None and trimestre_update.code != db_trimestre.code:
                self._check_code_exists(trimestre_update.code)
            update_data = trimestre_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_trimestre, key, value)
            new_trimestre = self.trimestre_repository.save(db_trimestre)
            self.trimestre_repository.session.commit()
            return new_trimestre
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.trimestre_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du trimestre: {str(e)}")

    def delete_trimestre(self, trimestre_id: int):
        """Supprime un trimestre en BD"""
        try:
            db_trimestre = self.trimestre_repository.findOne(trimestre_id)
            self._check_trimestre_exists(db_trimestre)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une section durant une annee scolaire en cours"
                    }
                )
            delete_trimestre = self.trimestre_repository.deleteOne(
                trimestre_id)
            if delete_trimestre:
                return {
                    "success": True,
                    "detail": {"id": trimestre_id, "message": "Trimestre supprimé"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": trimestre_id, "message": "Trimestre non supprimé"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.trimestre_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du trimestre: {str(e)}")

    def get_one_trimestre(self, trimestre_id: int):
        """Récupère un trimestre en BD"""
        try:
            db_trimestre = self.trimestre_repository.findOne(trimestre_id)
            self._check_trimestre_exists(db_trimestre)
            return db_trimestre
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.trimestre_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération du trimestre: {str(e)}")

    def get_all_trimestre(self):
        """Récupère tous les trimestres en BD"""
        try:
            db_trimestres = self.trimestre_repository.findAll()
            return db_trimestres
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.trimestre_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des trimestres: {str(e)}")
