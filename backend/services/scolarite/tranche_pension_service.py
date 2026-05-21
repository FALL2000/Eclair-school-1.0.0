from fastapi import HTTPException

from models.scolarite.tranche_pension import TranchePension
from repositories.scolarite.tranche_pension_repository import TranchePensionRepository
from schemas.scolarite.tranche_pension_dto import (
    TranchePensionBulkCreateDTO,
    TranchePensionBulkUpdateDTO,
    TranchePensionCreateDTO,
    TranchePensionUpdateDTO,
)


class TranchePensionService:
    def __init__(self, tranche_repository: TranchePensionRepository):
        self.tranche_repository = tranche_repository

    def _session(self):
        return self.tranche_repository.session

    def _check_code_exists(self, code: str):
        exist = self.tranche_repository.findByCode(code)
        if len(exist) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La tranche avec le code {code} existe déjà."
                }
            )

    def _check_numero_ordre_exists(self, id_niveau: int, numero_ordre: int):
        exist = self.tranche_repository.findBy(id_niveau=id_niveau, numero_ordre=numero_ordre)
        if len(exist) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_NUMERO_ORDRE",
                    "message": f"Une tranche avec le numéro d'ordre {numero_ordre} existe déjà pour ce niveau."
                }
            )

    def _check_tranche_exists(self, db_tranche: TranchePension | None):
        if db_tranche is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "TRANCHE_PENSION_NOT_FOUND",
                    "message": "Tranche pension non trouvée"
                }
            )

    def get_all_tranches(self):
        """Recupere toutes les tranches pension en BD"""
        try:
            return self.tranche_repository.findAll()
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des tranches: {str(e)}")

    def get_one_tranche(self, tranche_id: int):
        """Recupere une tranche pension en BD"""
        try:
            db_tranche = self.tranche_repository.findOne(tranche_id)
            self._check_tranche_exists(db_tranche)
            return db_tranche
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de la tranche: {str(e)}")

    def get_tranches_by_niveau(self, id_niveau: int):
        """Recupere les tranches pension d'un niveau en BD"""
        try:
            return self.tranche_repository.findBy(id_niveau=id_niveau)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des tranches par niveau: {str(e)}")

    def add_tranche(self, tranche_in: TranchePensionCreateDTO, id_niveau: int):
        """Ajoute une tranche pension en BD"""
        try:
            self._check_code_exists(tranche_in.code)
            self._check_numero_ordre_exists(id_niveau, tranche_in.numero_ordre)
            tranche_dict = tranche_in.model_dump()
            tranche_dict["id_niveau"] = id_niveau
            db_tranche = TranchePension.model_validate(tranche_dict)
            new_tranche = self.tranche_repository.save(db_tranche)
            self._session().commit()
            return new_tranche
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la tranche: {str(e)}")

    def add_bulk_tranches(self, data: TranchePensionBulkCreateDTO, id_niveau: int):
        """Ajoute plusieurs tranches pension en masse pour un niveau en BD"""
        try:
            codes = [t.code for t in data.tranches]
            if len(codes) != len(set(codes)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_CODE_IN_REQUEST",
                        "message": "Des codes dupliqués sont présents dans la liste"
                    }
                )
            ordres = [t.numero_ordre for t in data.tranches]
            if len(ordres) != len(set(ordres)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_ORDRE_IN_REQUEST",
                        "message": "Des numéros d'ordre dupliqués sont présents dans la liste"
                    }
                )
            for tranche in data.tranches:
                self._check_code_exists(tranche.code)
                self._check_numero_ordre_exists(id_niveau, tranche.numero_ordre)

            data_list = [
                {**t.model_dump(), "id_niveau": id_niveau}
                for t in data.tranches
            ]
            self.tranche_repository.InsertMany(data_list)
            self._session().commit()
            return self.tranche_repository.findBy(id_niveau=id_niveau)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout en masse des tranches: {str(e)}")

    def update_tranche(self, tranche_id: int, tranche_update: TranchePensionUpdateDTO):
        """Modifie une tranche pension en BD"""
        try:
            db_tranche = self.tranche_repository.findOne(tranche_id)
            self._check_tranche_exists(db_tranche)
            if tranche_update.code is not None and tranche_update.code != db_tranche.code:
                self._check_code_exists(tranche_update.code)
            if tranche_update.numero_ordre is not None and tranche_update.numero_ordre != db_tranche.numero_ordre:
                self._check_numero_ordre_exists(db_tranche.id_niveau, tranche_update.numero_ordre)
            update_data = tranche_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_tranche, key, value)
            updated = self.tranche_repository.save(db_tranche)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la tranche: {str(e)}")

    def update_bulk_tranches(self, data: TranchePensionBulkUpdateDTO):
        """Modifie plusieurs tranches pension en masse en BD"""
        try:
            for item in data.tranches:
                db_tranche = self.tranche_repository.findOne(item.id)
                self._check_tranche_exists(db_tranche)
                if item.code is not None and item.code != db_tranche.code:
                    self._check_code_exists(item.code)
                if item.numero_ordre is not None and item.numero_ordre != db_tranche.numero_ordre:
                    self._check_numero_ordre_exists(db_tranche.id_niveau, item.numero_ordre)
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    self.tranche_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            ids = [item.id for item in data.tranches]
            return [self.tranche_repository.findOne(id) for id in ids]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification en masse des tranches: {str(e)}")

    def delete_tranche(self, tranche_id: int):
        """Supprime une tranche pension en BD"""
        try:
            db_tranche = self.tranche_repository.findOne(tranche_id)
            self._check_tranche_exists(db_tranche)
            deleted = self.tranche_repository.deleteOne(tranche_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": tranche_id, "message": "Tranche pension supprimée"}
                }
            return {
                "success": False,
                "detail": {"id": tranche_id, "message": "Tranche pension non supprimée"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la tranche: {str(e)}")
