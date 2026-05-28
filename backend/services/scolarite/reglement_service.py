from datetime import date

from fastapi import HTTPException

from models.inscription.inscription import Inscription
from models.scolarite.reglement import Reglement
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.scolarite.reglement_repository import ReglementRepository
from schemas.scolarite.reglement_dto import (
    PaginatedReglement,
    ReglementCreateDTO,
    ReglementParClasseResponseDTO,
    ReglementResponseDTO,
    ReglementUpdateDTO,
)
from services.administration.annee_service import AnneeService


class ReglementService:
    def __init__(
        self,
        reglement_repository: ReglementRepository,
        annee_repository: AnneeRepository,
        classe_repository: ClasseRepository,
    ):
        self.reglement_repository = reglement_repository
        self.annee_repository = annee_repository
        self.classe_repository = classe_repository

    def _session(self):
        return self.reglement_repository.session

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    def _check_reglement_exists(self, db_reglement: Reglement | None):
        if db_reglement is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "REGLEMENT_NOT_FOUND",
                    "message": "Règlement non trouvé",
                },
            )

    def add_reglement(self, reglement_in: ReglementCreateDTO, id_eleve: int, id_tranche_pension: int, current_user: dict):
        """Enregistre un règlement pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            reglement_dict = reglement_in.model_dump()
            reglement_dict["id_eleve"] = id_eleve
            reglement_dict["id_tranche_pension"] = id_tranche_pension
            reglement_dict["id_annee"] = annee.id
            reglement_dict["id_user"] = current_user["id"]
            reglement_dict["date_reglement"] = date.today()
            db_reglement = Reglement.model_validate(reglement_dict)
            new_reglement = self.reglement_repository.save(db_reglement)
            self._session().commit()
            self._session().refresh(new_reglement)
            return new_reglement
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du règlement: {str(e)}")

    def update_reglement(self, reglement_id: int, reglement_update: ReglementUpdateDTO):
        """Modifie un règlement en BD"""
        try:
            db_reglement = self.reglement_repository.findOne(reglement_id)
            self._check_reglement_exists(db_reglement)
            update_data = reglement_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reglement, key, value)
            updated = self.reglement_repository.save(db_reglement)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du règlement: {str(e)}")

    def delete_reglement(self, reglement_id: int):
        """Supprime un règlement — impossible durant une année scolaire en cours"""
        try:
            if len(self.annee_repository.findByIs_cloture(False)) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un règlement durant une année scolaire en cours",
                    },
                )
            db_reglement = self.reglement_repository.findOne(reglement_id)
            self._check_reglement_exists(db_reglement)
            deleted = self.reglement_repository.deleteOne(reglement_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": reglement_id, "message": "Règlement supprimé"}}
            return {"success": False, "detail": {"id": reglement_id, "message": "Règlement non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du règlement: {str(e)}")

    def get_all_reglements(self, page: int | None, page_size: int | None) -> PaginatedReglement:
        """Récupère tous les règlements paginés, triés par date décroissante"""
        try:
            total_items = self.reglement_repository.count_all()
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = (total_items + page_size - 1) // page_size
            if total_pages == 0:
                total_pages = 1
            if page > total_pages:
                page = total_pages
            items = self.reglement_repository.find_all_ordered_desc(
                limit=page_size,
                offset=(page - 1) * page_size,
            ) if page > 0 else []
            return PaginatedReglement(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                reglements=items,
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des règlements: {str(e)}")

    def get_reglements_by_classe(self, id_classe: int) -> list[ReglementParClasseResponseDTO]:
        """Récupère les règlements des élèves inscrits dans une classe pour l'année en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            classe = self.classe_repository.findOne(id_classe)
            if classe is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "CLASSE_NOT_FOUND",
                        "message": "Classe non trouvée",
                    },
                )
            inscriptions = classe.inscriptions.filter(
                Inscription.id_annee == annee.id, Inscription.is_inscris == True
            ).all()

            reglements = []
            for inscription in inscriptions:
                eleve_reglements = [
                    r for r in inscription.eleve.reglements
                    if r.id_annee == annee.id
                ]
                reglements.extend(eleve_reglements)

            return reglements
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des règlements par classe: {str(e)}")
