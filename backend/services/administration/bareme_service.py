from fastapi import HTTPException

from models.administration.bareme import Bareme
from repositories.administration.bareme_repository import BaremeRepository
from schemas.administration.bareme_dto import BaremeCreateDTO, BaremeUpdateDTO


class BaremeService:
    def __init__(self, bareme_repository: BaremeRepository):
        self.bareme_repository = bareme_repository

    def _session(self):
        return self.bareme_repository.session

    def _check_code_exists(self, code: str):
        exist_bareme = self.bareme_repository.findByCode(code)
        if len(exist_bareme) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"Le barème avec le code {code} existe déjà."
                }
            )

    def _check_bareme_exists(self, db_bareme: Bareme | None):
        if db_bareme is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "BAREME_NOT_FOUND",
                    "message": "Barème non trouvé"
                }
            )

    def add_bareme(self, bareme_in: BaremeCreateDTO):
        """Ajoute un barème de notation en BD"""
        try:
            self._check_code_exists(bareme_in.code)
            db_bareme = Bareme.model_validate(bareme_in)
            new_bareme = self.bareme_repository.save(db_bareme)
            self._session().commit()
            return new_bareme
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du barème: {str(e)}")

    def update_bareme(self, bareme_update: BaremeUpdateDTO, bareme_id: int):
        """Modifie un barème de notation en BD"""
        try:
            db_bareme = self.bareme_repository.findOne(bareme_id)
            self._check_bareme_exists(db_bareme)
            if bareme_update.code is not None and bareme_update.code != db_bareme.code:
                self._check_code_exists(bareme_update.code)
            if bareme_update.valeur_max is not None:
                depassements = [
                    a for a in db_bareme.appreciations if a.valeur_max > bareme_update.valeur_max
                ]
                if len(depassements) > 0:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "APPRECIATION_HORS_BAREME",
                            "message": (
                                f"Impossible de réduire la note maximale à {bareme_update.valeur_max} : "
                                f"l'appréciation {depassements[0].libelle} va jusqu'à {depassements[0].valeur_max}"
                            )
                        }
                    )
            update_data = bareme_update.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(db_bareme, key, value)
            new_bareme = self.bareme_repository.save(db_bareme)
            self._session().commit()
            return new_bareme
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du barème: {str(e)}")

    def delete_bareme(self, bareme_id: int):
        """Supprime un barème de notation en BD — impossible s'il est utilisé"""
        try:
            db_bareme = self.bareme_repository.findOne(bareme_id)
            self._check_bareme_exists(db_bareme)
            if len(db_bareme.matieres_evaluees) > 0 or len(db_bareme.appreciations) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un barème lié à des matières évaluées ou à des appréciations"
                    }
                )
            deleted = self.bareme_repository.deleteOne(bareme_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": bareme_id, "message": "Barème supprimé"}
                }
            return {
                "success": False,
                "detail": {"id": bareme_id, "message": "Barème non supprimé"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du barème: {str(e)}")

    def get_one_bareme(self, bareme_id: int):
        """Récupère un barème de notation en BD"""
        try:
            db_bareme = self.bareme_repository.findOne(bareme_id)
            self._check_bareme_exists(db_bareme)
            return db_bareme
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération du barème: {str(e)}")

    def get_all_baremes(self):
        """Récupère tous les barèmes de notation en BD"""
        try:
            return self.bareme_repository.findAll()
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des barèmes: {str(e)}")
