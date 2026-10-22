from fastapi import HTTPException

from schemas.administration.appreciation_dto import AppreciationCreateDTO, AppreciationUpdateDTO
from repositories.administration.appreciation_repository import AppreciationRepository
from repositories.administration.bareme_repository import BaremeRepository
from models.administration.appreciation import Appreciation
from models.administration.bareme import Bareme


class AppreciationService:
    def __init__(self, appreciation_repository: AppreciationRepository, bareme_repository: BaremeRepository):
        self.appreciation_repository = appreciation_repository
        self.bareme_repository = bareme_repository

    def _check_libelle_exists(self, libelle: str, id_bareme: int):
        exist_appreciation = self.appreciation_repository.findBy(
            load_relations=False, libelle=libelle, id_bareme=id_bareme)
        if len(exist_appreciation) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L' appreciation avec le libelle {libelle} existe déjà pour ce barème."
                }
            )

    def _check_appreciation_exists(self, db_appreciation: Appreciation | None):
        if db_appreciation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "APPRECIATION_NOT_FOUND",
                    "message": "appreciation non trouvé"
                }
            )

    def _get_bareme(self, id_bareme: int) -> Bareme:
        db_bareme = self.bareme_repository.findOne(id_bareme, load_relations=False)
        if db_bareme is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "BAREME_NOT_FOUND",
                    "message": "Barème non trouvé"
                }
            )
        return db_bareme

    def _check_intervalle(self, valeur_min: float, valeur_max: float, db_bareme: Bareme, appreciation_id: int | None = None):
        """Vérifie que l'intervalle fermé [valeur_min, valeur_max] est valide, compris dans [0, note maximale du barème]
        et qu'il ne chevauche pas celui d'une autre appréciation du même barème"""
        if valeur_min > valeur_max:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INTERVALLE_INVALIDE",
                    "message": "La valeur minimale doit être inférieure ou égale à la valeur maximale"
                }
            )
        if valeur_min < 0 or valeur_max > db_bareme.valeur_max:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INTERVALLE_HORS_BAREME",
                    "message": f"L'intervalle doit être compris entre 0 et {db_bareme.valeur_max} (barème {db_bareme.libelle})"
                }
            )
        chevauchements = [
            a for a in self.appreciation_repository.find_chevauchement(db_bareme.id, valeur_min, valeur_max)
            if a.id != appreciation_id
        ]
        if len(chevauchements) > 0:
            appreciation = chevauchements[0]
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "INTERVALLE_CHEVAUCHEMENT",
                    "message": (
                        f"L'intervalle [{valeur_min}, {valeur_max}] chevauche celui de l'appréciation "
                        f"{appreciation.libelle} [{appreciation.valeur_min}, {appreciation.valeur_max}]"
                    )
                }
            )

    def add_appreciation(self, appreciation_in: AppreciationCreateDTO, id_bareme: int):
        """Ajoute une appreciation en BD"""
        try:
            db_bareme = self._get_bareme(id_bareme)
            self._check_libelle_exists(appreciation_in.libelle, id_bareme)
            self._check_intervalle(appreciation_in.valeur_min, appreciation_in.valeur_max, db_bareme)
            appreciation_dict = appreciation_in.model_dump()
            appreciation_dict["id_bareme"] = id_bareme
            db_appreciation = Appreciation.model_validate(appreciation_dict)
            new_appreciation = self.appreciation_repository.save(
                db_appreciation)
            self.appreciation_repository.session.commit()
            return new_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de l'appreciation: {str(e)}")

    def update_appreciation(self, appreciation_update: AppreciationUpdateDTO, appreciation_id: int):
        """Modifie une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            update_data = appreciation_update.model_dump(exclude_unset=True, exclude_none=True)
            id_bareme = update_data.get("id_bareme", db_appreciation.id_bareme)
            db_bareme = self._get_bareme(id_bareme)
            libelle = update_data.get("libelle", db_appreciation.libelle)
            if libelle != db_appreciation.libelle or id_bareme != db_appreciation.id_bareme:
                self._check_libelle_exists(libelle, id_bareme)
            self._check_intervalle(
                update_data.get("valeur_min", db_appreciation.valeur_min),
                update_data.get("valeur_max", db_appreciation.valeur_max),
                db_bareme,
                appreciation_id,
            )
            for key, value in update_data.items():
                setattr(db_appreciation, key, value)
            new_appreciation = self.appreciation_repository.save(
                db_appreciation)
            self.appreciation_repository.session.commit()
            return new_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'appreciation: {str(e)}")

    def delete_appreciation(self, appreciation_id: int):
        """Supprime une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            delete_appreciation = self.appreciation_repository.deleteOne(
                appreciation_id)
            if delete_appreciation:
                self.appreciation_repository.session.commit()
                return {
                    "success": True,
                    "detail": {"id": appreciation_id, "message": "appreciation supprimée"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": appreciation_id, "message": "appreciation non supprimée"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'appreciation: {str(e)}")

    def get_one_appreciation(self, appreciation_id: int):
        """Récupère une appreciation en BD"""
        try:
            db_appreciation = self.appreciation_repository.findOne(
                appreciation_id)
            self._check_appreciation_exists(db_appreciation)
            return db_appreciation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de l'appreciation: {str(e)}")

    def get_all_appreciation(self, id_bareme: int | None = None):
        """Récupère toutes les appreciations en BD, éventuellement filtrées par barème"""
        try:
            if id_bareme is not None:
                return self.appreciation_repository.findBy(id_bareme=id_bareme)
            db_appreciations = self.appreciation_repository.findAll()
            return db_appreciations
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.appreciation_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des appreciations: {str(e)}")
