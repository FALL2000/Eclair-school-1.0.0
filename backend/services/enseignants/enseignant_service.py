from fastapi import HTTPException

from models.enseignants.enseignant import Enseignant
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignants.enseignant_repository import EnseignantRepository
from schemas.enseignants.enseignant_dto import (
    EnseignantBulkUpdateDTO,
    EnseignantDetailResponseDTO,
    EnseignantResponseDTO,
    EnseignantUpdateDTO,
    PaginatedEnseignant,
)


class EnseignantService:
    def __init__(
        self,
        enseignant_repository: EnseignantRepository,
        annee_repository: AnneeRepository,
    ):
        self.enseignant_repository = enseignant_repository
        self.annee_repository = annee_repository

    def _session(self):
        return self.enseignant_repository.session

    def _check_enseignant_exists(self, db_enseignant: Enseignant | None):
        if db_enseignant is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ENSEIGNANT_NOT_FOUND",
                    "message": "Enseignant non trouvé",
                },
            )

    def get_one_enseignant(self, enseignant_id: int) -> EnseignantDetailResponseDTO:
        """Récupère un enseignant avec ses enseignements"""
        try:
            db_enseignant = self.enseignant_repository.findOne(enseignant_id)
            self._check_enseignant_exists(db_enseignant)
            return db_enseignant
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de l'enseignant: {str(e)}")

    def get_all_enseignants(self, page: int | None, page_size: int | None) -> PaginatedEnseignant:
        """Récupère tous les enseignants avec pagination"""
        try:
            total_items = self.enseignant_repository.count_all()
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = (total_items + page_size - 1) // page_size
            if total_pages == 0:
                total_pages = 1
            if page > total_pages:
                page = total_pages
            items = self.enseignant_repository.findAll(
                limit=page_size,
                offset=(page - 1) * page_size,
            ) if page > 0 else []
            return PaginatedEnseignant(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                enseignants=items,
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des enseignants: {str(e)}")

    def update_enseignant(self, enseignant_id: int, data: EnseignantUpdateDTO) -> EnseignantResponseDTO:
        """Modifie un enseignant en BD"""
        try:
            db_enseignant = self.enseignant_repository.findOne(enseignant_id)
            self._check_enseignant_exists(db_enseignant)
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_enseignant, key, value)
            updated = self.enseignant_repository.save(db_enseignant)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'enseignant: {str(e)}")

    def update_bulk_enseignants(self, data: EnseignantBulkUpdateDTO) -> list[EnseignantResponseDTO]:
        """Modifie plusieurs enseignants en masse en BD"""
        try:
            for item in data.enseignants:
                db_enseignant = self.enseignant_repository.findOne(item.id)
                self._check_enseignant_exists(db_enseignant)
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    self.enseignant_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            return [self.enseignant_repository.findOne(item.id) for item in data.enseignants]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification en masse des enseignants: {str(e)}")

    def delete_enseignant(self, enseignant_id: int):
        """Supprime un enseignant — impossible durant une année scolaire en cours"""
        try:
            if len(self.annee_repository.findByIs_cloture(False)) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un enseignant durant une année scolaire en cours",
                    },
                )
            db_enseignant = self.enseignant_repository.findOne(enseignant_id)
            self._check_enseignant_exists(db_enseignant)
            deleted = self.enseignant_repository.deleteOne(enseignant_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": enseignant_id, "message": "Enseignant supprimé"}}
            return {"success": False, "detail": {"id": enseignant_id, "message": "Enseignant non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'enseignant: {str(e)}")
