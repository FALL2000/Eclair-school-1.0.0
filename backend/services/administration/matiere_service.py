from fastapi import HTTPException

from models.administration.matiere import Matiere
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_repository import GroupeMatiereRepository
from repositories.administration.matiere_repository import MatiereRepository
from schemas.administration.matiere_dto import MatiereCreateDTO, MatiereUpdateDTO


class MatiereService:
    def __init__(
        self,
        matiere_repository: MatiereRepository,
        groupe_matiere_repository: GroupeMatiereRepository,
        annee_repository: AnneeRepository,
    ):
        self.matiere_repository = matiere_repository
        self.groupe_matiere_repository = groupe_matiere_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_matiere = self.matiere_repository.findByCode(code)
        if len(exist_matiere) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La matiere avec le code {code} existe deja."
                }
            )

    def _check_matiere_exists(self, db_matiere: Matiere | None):
        if db_matiere is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "MATIERE_NOT_FOUND",
                    "message": "Matiere non trouvee"
                }
            )

    def _check_groupe_matiere_exists(self, groupe_matiere_id: int):
        if self.groupe_matiere_repository.findOne(groupe_matiere_id) is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "GROUPE_MATIERE_NOT_FOUND",
                    "message": "Groupe de matiere non trouve"
                }
            )

    def add_matiere(self, matiere_in: MatiereCreateDTO, groupe_matiere_id: int):
        try:
            self._check_code_exists(matiere_in.code)
            self._check_groupe_matiere_exists(groupe_matiere_id)
            db_matiere = Matiere.model_validate(matiere_in)
            db_matiere.id_groupe_matiere = groupe_matiere_id
            new_matiere = self.matiere_repository.save(db_matiere)
            self.matiere_repository.session.commit()
            return new_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la matiere: {str(e)}")

    def update_matiere(self, matiere_update: MatiereUpdateDTO, matiere_id: int):
        try:
            db_matiere = self.matiere_repository.findOne(matiere_id)
            self._check_matiere_exists(db_matiere)
            if matiere_update.code is not None and matiere_update.code != db_matiere.code:
                self._check_code_exists(matiere_update.code)
            update_data = matiere_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_matiere, key, value)
            new_matiere = self.matiere_repository.save(db_matiere)
            self.matiere_repository.session.commit()
            return new_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la matiere: {str(e)}")

    def delete_matiere(self, matiere_id: int):
        try:
            db_matiere = self.matiere_repository.findOne(matiere_id)
            self._check_matiere_exists(db_matiere)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une matiere durant une annee scolaire en cours"
                    }
                )
            delete_matiere = self.matiere_repository.deleteOne(matiere_id)
            if delete_matiere:
                return {
                    "success": True,
                    "detail": {"id": matiere_id, "message": "Matiere supprimee"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": matiere_id, "message": "Matiere non supprimee"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la matiere: {str(e)}")

    def get_one_matiere(self, matiere_id: int):
        try:
            db_matiere = self.matiere_repository.findOne(matiere_id)
            self._check_matiere_exists(db_matiere)
            return db_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de la matiere: {str(e)}")

    def get_all_matiere(self):
        try:
            db_matieres = self.matiere_repository.findAll()
            return db_matieres
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des matieres: {str(e)}")
