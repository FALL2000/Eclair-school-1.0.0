from fastapi import HTTPException

from models.administration.matiere_evalue import MatiereEvalue
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from schemas.administration.matiere_evalue_dto import MatiereEvalueCreateDTO, MatiereEvalueUpdateDTO


class MatiereEvalueService:
    def __init__(
        self,
        matiere_evalue_repository: MatiereEvalueRepository,
        groupe_matiere_evalue_repository: GroupeMatiereEvalueRepository,
        annee_repository: AnneeRepository,
    ):
        self.matiere_evalue_repository = matiere_evalue_repository
        self.groupe_matiere_evalue_repository = groupe_matiere_evalue_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_matiere_evalue = self.matiere_evalue_repository.findByCode(code)
        if len(exist_matiere_evalue) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La matiere evaluee avec le code {code} existe deja."
                }
            )

    def _check_matiere_evalue_exists(self, db_matiere_evalue: MatiereEvalue | None):
        if db_matiere_evalue is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "MATIERE_EVALUE_NOT_FOUND",
                    "message": "Matiere evaluee non trouvee"
                }
            )

    def _check_groupe_matiere_evalue_exists(self, groupe_matiere_evalue_id: int):
        if self.groupe_matiere_evalue_repository.findOne(groupe_matiere_evalue_id) is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "GROUPE_MATIERE_EVALUE_NOT_FOUND",
                    "message": "Groupe de matiere evalue non trouve"
                }
            )

    def add_matiere_evalue(self, matiere_evalue_in: MatiereEvalueCreateDTO, groupe_matiere_evalue_id: int):
        try:
            self._check_code_exists(matiere_evalue_in.code)
            self._check_groupe_matiere_evalue_exists(groupe_matiere_evalue_id)
            db_matiere_evalue = MatiereEvalue.model_validate(matiere_evalue_in)
            db_matiere_evalue.id_groupe_matiere = groupe_matiere_evalue_id
            new_matiere_evalue = self.matiere_evalue_repository.save(db_matiere_evalue)
            self.matiere_evalue_repository.session.commit()
            return new_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la matiere evaluee: {str(e)}")

    def update_matiere_evalue(self, matiere_evalue_update: MatiereEvalueUpdateDTO, matiere_evalue_id: int):
        try:
            db_matiere_evalue = self.matiere_evalue_repository.findOne(matiere_evalue_id)
            self._check_matiere_evalue_exists(db_matiere_evalue)
            if matiere_evalue_update.code is not None and matiere_evalue_update.code != db_matiere_evalue.code:
                self._check_code_exists(matiere_evalue_update.code)
            update_data = matiere_evalue_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_matiere_evalue, key, value)
            new_matiere_evalue = self.matiere_evalue_repository.save(db_matiere_evalue)
            self.matiere_evalue_repository.session.commit()
            return new_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la matiere evaluee: {str(e)}")

    def delete_matiere_evalue(self, matiere_evalue_id: int):
        try:
            db_matiere_evalue = self.matiere_evalue_repository.findOne(matiere_evalue_id)
            self._check_matiere_evalue_exists(db_matiere_evalue)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une matiere evaluee durant une annee scolaire en cours"
                    }
                )
            delete_matiere_evalue = self.matiere_evalue_repository.deleteOne(matiere_evalue_id)
            if delete_matiere_evalue:
                return {
                    "success": True,
                    "detail": {"id": matiere_evalue_id, "message": "Matiere evaluee supprimee"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": matiere_evalue_id, "message": "Matiere evaluee non supprimee"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la matiere evaluee: {str(e)}")

    def get_one_matiere_evalue(self, matiere_evalue_id: int):
        try:
            db_matiere_evalue = self.matiere_evalue_repository.findOne(matiere_evalue_id)
            self._check_matiere_evalue_exists(db_matiere_evalue)
            return db_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de la matiere evaluee: {str(e)}")

    def get_all_matiere_evalue(self):
        try:
            db_matieres_evaluees = self.matiere_evalue_repository.findAll()
            return db_matieres_evaluees
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des matieres evaluees: {str(e)}")
