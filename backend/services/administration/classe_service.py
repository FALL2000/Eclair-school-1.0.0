from fastapi import HTTPException

from repositories.administration.annee_repository import AnneeRepository
from schemas.administration.classe_dto import ClasseCreateDTO, ClasseUpdateDTO
from models.administration.classe import Classe
from repositories.administration.classe_repository import ClasseRepository


class ClasseService:
    def __init__(self, classe_repository: ClasseRepository, annee_repository: AnneeRepository):
        self.classe_repository = classe_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_classe = self.classe_repository.findByCode(code)
        if len(exist_classe) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La classe avec le code {code} existe déjà."
                }
            )

    def _check_classe_exists(self, db_classe: Classe | None):
        if db_classe is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "CLASSE_NOT_FOUND",
                    "message": "Classe non trouvée"
                }
            )

    def add_classe(self, classe_in: ClasseCreateDTO, niveau_id: int):
        """Ajoute une classe en BD"""
        try:
            self._check_code_exists(classe_in.code)
            db_classe = Classe.model_validate(classe_in)
            db_classe.id_niveau = niveau_id
            new_classe = self.classe_repository.save(db_classe)
            self.classe_repository.session.commit()
            return new_classe
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.classe_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la classe: {str(e)}")

    def update_classe(self, classe_update: ClasseUpdateDTO, classe_id: int):
        """Modifie une classe BD"""
        try:
            db_classe = self.classe_repository.findOne(classe_id)
            self._check_classe_exists(db_classe)
            if classe_update.code is not None and classe_update.code != db_classe.code:
                self._check_code_exists(classe_update.code)
            update_data = classe_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_classe, key, value)
            new_classe = self.classe_repository.save(db_classe)
            self.classe_repository.session.commit()
            return new_classe
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.classe_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la classe: {str(e)}")

    def delete_classe(self, classe_id: int):
        """Supprime une classe en BD"""
        try:
            db_classe = self.classe_repository.findOne(classe_id)
            self._check_classe_exists(db_classe)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une série durant une année scolaire en cours"
                    }
                )
            delete_classe = self.classe_repository.deleteOne(classe_id)
            if delete_classe:
                return {
                    "success": True,
                    "detail": {"id": classe_id, "message": "Classe supprimée"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": classe_id, "message": "Classe non supprimée"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.classe_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la classe: {str(e)}")

    def get_one_classe(self, classe_id: int):
        """Recupere une classe en BD"""
        try:
            db_classe = self.classe_repository.findOne(classe_id)
            self._check_classe_exists(db_classe)
            return db_classe
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.classe_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de la classe: {str(e)}")

    def get_all_classe(self):
        """Recupere toutes les classes en BD"""
        try:
            db_classes = self.classe_repository.findAll()
            return db_classes
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.classe_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des classes: {str(e)}")
