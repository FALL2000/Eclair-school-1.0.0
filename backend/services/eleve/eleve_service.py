from fastapi import HTTPException

from models.eleve.eleve import Eleve
from repositories.eleve.eleve_repository import EleveRepository
from schemas.eleve.eleve_dto import EleveUpdateDTO


class EleveService:
    def __init__(self, eleve_repository: EleveRepository):
        self.eleve_repository = eleve_repository

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
