from fastapi import HTTPException

from schemas.administration.cycle_dto import CycleCreateDTO, CycleUpdateDTO
from models.administration.cycle import Cycle
from repositories.administration.cycle_repository import CycleRepository
from repositories.administration.annee_repository import AnneeRepository


class CycleService:
    def __init__(self, cycle_repository: CycleRepository, annee_repository: AnneeRepository):
        self.cycle_repository = cycle_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_cycle = self.cycle_repository.findByCode(code)
        if len(exist_cycle) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"Le cycle avec le code {code} existe déjà."
                }
            )

    def _check_cycle_exists(self, db_cycle: Cycle | None):
        if db_cycle is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "cycle_NOT_FOUND",
                    "message": "cycle non trouve"
                }
            )

    def add_cycle(self, cycle_in: CycleCreateDTO, section_id: int):
        """Ajoute un cycle en BD"""
        try:
            self._check_code_exists(cycle_in.code)
            db_cycle = Cycle.model_validate(cycle_in)
            db_cycle.id_section = section_id
            new_cycle = self.cycle_repository.save(db_cycle)
            self.cycle_repository.session.commit()
            return new_cycle
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.cycle_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du cycle: {str(e)}")

    def update_cycle(self, cycle_update: CycleUpdateDTO, cycle_id: int):
        """Modifie un cycle BD"""
        try:
            db_cycle = self.cycle_repository.findOne(cycle_id)
            self._check_cycle_exists(db_cycle)
            if cycle_update.code is not None and cycle_update.code != db_cycle.code:
                self._check_code_exists(cycle_update.code)
            update_data = cycle_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_cycle, key, value)
            new_cycle = self.cycle_repository.save(db_cycle)
            self.cycle_repository.session.commit()
            return new_cycle
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.cycle_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification  du cycle: {str(e)}")

    def delete_cycle(self, cycle_id: int):
        """Supprime un cycle en BD"""
        try:
            db_cycle = self.cycle_repository.findOne(cycle_id)
            self._check_cycle_exists(db_cycle)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un cycle durant une annee scolaire en cours"
                    }
                )
            delete_cycle = self.cycle_repository.deleteOne(cycle_id)
            if delete_cycle:
                return {
                    "success": True,
                    "detail": {"id": cycle_id, "message": "cycle supprimé"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": cycle_id, "message": "cycle non supprimé"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.cycle_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression  du cycle: {str(e)}")

    def get_one_cycle(self, cycle_id: int):
        """Recupere un cycle en BD"""
        try:
            db_cycle = self.cycle_repository.findOne(cycle_id)
            self._check_cycle_exists(db_cycle)
            return db_cycle
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.cycle_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation  du cycle: {str(e)}")

    def get_all_cycle(self):
        """Recupere tous les cycles en BD"""
        try:
            db_cycles = self.cycle_repository.findAll()
            return db_cycles
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.cycle_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation  des cycles: {str(e)}")
