from fastapi import HTTPException

from models.administration.annee import Annee
from schemas.administration.annee_dto import AnneeCreateDTO, AnneeUpdateDTO
from repositories.administration.annee_repository import AnneeRepository


class AnneeService:
    def __init__(self, annee_repository: AnneeRepository):
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_annee = self.annee_repository.findByCode(code)
        if len(exist_annee) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L'année avec le code {code} existe déjà."
                }
            )

    def define_annee_scolaire(self, annee_in: AnneeCreateDTO):
        """Defini une annee scolaire en BD"""
        try:
            self._check_code_exists(annee_in.code)
            db_annee = Annee.model_validate(annee_in)
            new_annee = self.annee_repository.save(db_annee)
            self.annee_repository.session.commit()
            return new_annee
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.annee_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la definition  de l'annee: {str(e)}")

    def update_annee_scolaire(self, annee_update: AnneeUpdateDTO, annee_id: int):
        """Modifie une annee definie en BD"""
        try:
            db_annee = self.annee_repository.findOne(annee_id)
            if db_annee is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "ANNEE_NOT_FOUND",
                        "message": "Annee non trouve"
                    }
                )
            if len(db_annee.inscriptions) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "INSCRIPTIONS_IN_ANNEE",
                        "message": "Modification impossible : des inscriptions sont déjà liées à cette année."
                    }
                )
            if annee_update.code is not None and annee_update.code != db_annee.code:
                self._check_code_exists(annee_update.code)
            update_data = annee_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_annee, key, value)
            new_annee = self.annee_repository.save(db_annee)
            self.annee_repository.session.commit()
            return new_annee
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.annee_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification  de l'annee: {str(e)}")
