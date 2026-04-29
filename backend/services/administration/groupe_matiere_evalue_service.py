from fastapi import HTTPException

from models.administration.groupe_matiere_evalue import GroupeMatiereEvalue
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.niveau_repository import NiveauRepository
from schemas.administration.groupe_matiere_evalues_dto import (
    GroupeMatiereEvalueCreateDTO,
    GroupeMatiereEvalueUpdateDTO,
)


class GroupeMatiereEvalueService:
    def __init__(
        self,
        groupe_matiere_evalue_repository: GroupeMatiereEvalueRepository,
        niveau_repository: NiveauRepository,
        annee_repository: AnneeRepository,
    ):
        self.groupe_matiere_evalue_repository = groupe_matiere_evalue_repository
        self.niveau_repository = niveau_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.findByCode(code)
        if len(exist_groupe_matiere_evalue) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"Le groupe de matiere evalue avec le code {code} existe deja."
                }
            )

    def _check_groupe_matiere_evalue_exists(self, db_groupe_matiere_evalue: GroupeMatiereEvalue | None):
        if db_groupe_matiere_evalue is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "GROUPE_MATIERE_EVALUE_NOT_FOUND",
                    "message": "Groupe de matiere evalue non trouve"
                }
            )

    def _check_niveau_exists(self, niveau_id: int):
        if self.niveau_repository.findOne(niveau_id) is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "NIVEAU_NOT_FOUND",
                    "message": "Niveau non trouve"
                }
            )

    def add_groupe_matiere_evalue(self, groupe_matiere_evalue_in: GroupeMatiereEvalueCreateDTO, niveau_id: int):
        try:
            self._check_code_exists(groupe_matiere_evalue_in.code)
            self._check_niveau_exists(niveau_id)
            db_groupe_matiere_evalue = GroupeMatiereEvalue.model_validate(groupe_matiere_evalue_in)
            db_groupe_matiere_evalue.id_niveau = niveau_id
            new_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.save(db_groupe_matiere_evalue)
            self.groupe_matiere_evalue_repository.session.commit()
            return new_groupe_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du groupe de matiere evalue: {str(e)}")

    def update_groupe_matiere_evalue(
        self, groupe_matiere_evalue_update: GroupeMatiereEvalueUpdateDTO, groupe_matiere_evalue_id: int
    ):
        try:
            db_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.findOne(groupe_matiere_evalue_id)
            self._check_groupe_matiere_evalue_exists(db_groupe_matiere_evalue)
            if (
                groupe_matiere_evalue_update.code is not None
                and groupe_matiere_evalue_update.code != db_groupe_matiere_evalue.code
            ):
                self._check_code_exists(groupe_matiere_evalue_update.code)
            update_data = groupe_matiere_evalue_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_groupe_matiere_evalue, key, value)
            new_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.save(db_groupe_matiere_evalue)
            self.groupe_matiere_evalue_repository.session.commit()
            return new_groupe_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du groupe de matiere evalue: {str(e)}")

    def delete_groupe_matiere_evalue(self, groupe_matiere_evalue_id: int):
        try:
            db_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.findOne(groupe_matiere_evalue_id)
            self._check_groupe_matiere_evalue_exists(db_groupe_matiere_evalue)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un groupe de matiere evalue durant une annee scolaire en cours"
                    }
                )
            delete_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.deleteOne(groupe_matiere_evalue_id)
            if delete_groupe_matiere_evalue:
                return {
                    "success": True,
                    "detail": {"id": groupe_matiere_evalue_id, "message": "Groupe de matiere evalue supprime"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": groupe_matiere_evalue_id, "message": "Groupe de matiere evalue non supprime"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du groupe de matiere evalue: {str(e)}")

    def get_one_groupe_matiere_evalue(self, groupe_matiere_evalue_id: int):
        try:
            db_groupe_matiere_evalue = self.groupe_matiere_evalue_repository.findOne(groupe_matiere_evalue_id)
            self._check_groupe_matiere_evalue_exists(db_groupe_matiere_evalue)
            return db_groupe_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la recuperation du groupe de matiere evalue: {str(e)}",
            )

    def get_all_groupe_matiere_evalue(self):
        try:
            db_groupes_matiere_evalue = self.groupe_matiere_evalue_repository.findAll()
            return db_groupes_matiere_evalue
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_evalue_repository.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la recuperation des groupes de matiere evalue: {str(e)}",
            )
