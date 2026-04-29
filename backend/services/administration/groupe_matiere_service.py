from fastapi import HTTPException

from models.administration.groupe_matiere import GroupeMatiere
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.groupe_matiere_repository import GroupeMatiereRepository
from schemas.administration.groupe_matiere_dto import GroupeMatiereCreateDTO, GroupeMatiereUpdateDTO


class GroupeMatiereService:
    def __init__(self, groupe_matiere_repository: GroupeMatiereRepository, annee_repository: AnneeRepository):
        self.groupe_matiere_repository = groupe_matiere_repository
        self.annee_repository = annee_repository

    def _check_libelle_exists(self, libelle: str):
        exist_groupe_matiere = self.groupe_matiere_repository.findByLibelle(libelle)
        if len(exist_groupe_matiere) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_LIBELLE",
                    "message": f"Le groupe de matiere avec le libelle {libelle} existe deja."
                }
            )

    def _check_groupe_matiere_exists(self, db_groupe_matiere: GroupeMatiere | None):
        if db_groupe_matiere is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "GROUPE_MATIERE_NOT_FOUND",
                    "message": "Groupe de matiere non trouve"
                }
            )

    def add_groupe_matiere(self, groupe_matiere_in: GroupeMatiereCreateDTO):
        try:
            self._check_libelle_exists(groupe_matiere_in.libelle)
            db_groupe_matiere = GroupeMatiere.model_validate(groupe_matiere_in)
            new_groupe_matiere = self.groupe_matiere_repository.save(db_groupe_matiere)
            self.groupe_matiere_repository.session.commit()
            return new_groupe_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du groupe de matiere: {str(e)}")

    def update_groupe_matiere(self, groupe_matiere_update: GroupeMatiereUpdateDTO, groupe_matiere_id: int):
        try:
            db_groupe_matiere = self.groupe_matiere_repository.findOne(groupe_matiere_id)
            self._check_groupe_matiere_exists(db_groupe_matiere)
            if groupe_matiere_update.libelle is not None and groupe_matiere_update.libelle != db_groupe_matiere.libelle:
                self._check_libelle_exists(groupe_matiere_update.libelle)
            update_data = groupe_matiere_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_groupe_matiere, key, value)
            new_groupe_matiere = self.groupe_matiere_repository.save(db_groupe_matiere)
            self.groupe_matiere_repository.session.commit()
            return new_groupe_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du groupe de matiere: {str(e)}")

    def delete_groupe_matiere(self, groupe_matiere_id: int):
        try:
            db_groupe_matiere = self.groupe_matiere_repository.findOne(groupe_matiere_id)
            self._check_groupe_matiere_exists(db_groupe_matiere)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un groupe de matiere durant une annee scolaire en cours"
                    }
                )
            delete_groupe_matiere = self.groupe_matiere_repository.deleteOne(groupe_matiere_id)
            if delete_groupe_matiere:
                return {
                    "success": True,
                    "detail": {"id": groupe_matiere_id, "message": "Groupe de matiere supprime"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": groupe_matiere_id, "message": "Groupe de matiere non supprime"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du groupe de matiere: {str(e)}")

    def get_one_groupe_matiere(self, groupe_matiere_id: int):
        try:
            db_groupe_matiere = self.groupe_matiere_repository.findOne(groupe_matiere_id)
            self._check_groupe_matiere_exists(db_groupe_matiere)
            return db_groupe_matiere
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du groupe de matiere: {str(e)}")

    def get_all_groupe_matiere(self):
        try:
            db_groupe_matieres = self.groupe_matiere_repository.findAll()
            return db_groupe_matieres
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.groupe_matiere_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des groupes de matieres: {str(e)}")
