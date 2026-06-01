from fastapi import HTTPException

from models.enseignement.cours import Cours
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignement.cours_repository import CoursRepository
from schemas.enseignement.cours_dto import (
    CoursCreateDTO,
    CoursBulkCreateDTO,
    CoursBulkUpdateDTO,
    CoursParClasseResponseDTO,
    CoursParEnseignantResponseDTO,
    CoursResponseDTO,
    CoursUpdateDTO,
)
from services.administration.annee_service import AnneeService


class CoursService:
    def __init__(
        self,
        cours_repository: CoursRepository,
        annee_repository: AnneeRepository,
    ):
        self.cours_repository = cours_repository
        self.annee_repository = annee_repository

    def _session(self):
        return self.cours_repository.session

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    def _check_cours_exists(self, db_cours: Cours | None):
        if db_cours is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "COURS_NOT_FOUND",
                    "message": "Cours non trouvé",
                },
            )

    def _check_periode_classe(self, jour: str, heure_deb, heure_fin, id_classe: int, id_annee: int):
        existing = self.cours_repository.findBy(
            jour=jour, heure_deb=heure_deb, heure_fin=heure_fin,
            id_classe=id_classe, id_annee=id_annee,
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "COURS_PERIODE_CLASSE_CONFLICT",
                    "message": "Un cours existe déjà à cette période dans cette classe",
                },
            )

    def _check_enseignant_periode(self, jour: str, heure_deb, heure_fin, id_enseignant: int, id_annee: int):
        existing = self.cours_repository.findBy(
            jour=jour, heure_deb=heure_deb, heure_fin=heure_fin,
            id_enseignant=id_enseignant, id_annee=id_annee,
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "ENSEIGNANT_PERIODE_CONFLICT",
                    "message": "L'enseignant a déjà un cours à cette période dans une autre classe",
                },
            )

    def add_cours(
        self,
        data: CoursCreateDTO,
        id_enseignant: int,
        id_classe: int,
        id_matiere: int,
    ) -> CoursResponseDTO:
        """Ajoute un cours en vérifiant les conflits de période"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            self._check_periode_classe(data.jour, data.heure_deb, data.heure_fin, id_classe, annee.id)
            self._check_enseignant_periode(data.jour, data.heure_deb, data.heure_fin, id_enseignant, annee.id)
            cours_dict = data.model_dump()
            cours_dict["id_enseignant"] = id_enseignant
            cours_dict["id_classe"] = id_classe
            cours_dict["id_annee"] = annee.id
            cours_dict["id_matiere"] = id_matiere
            db_cours = Cours.model_validate(cours_dict)
            new_cours = self.cours_repository.save(db_cours)
            self._session().commit()
            return new_cours
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du cours: {str(e)}")

    def add_bulk_cours(self, data: CoursBulkCreateDTO) -> list[CoursResponseDTO]:
        """Ajoute plusieurs cours en masse en vérifiant les conflits de période"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            new_cours_list = []
            for item in data.cours:
                self._check_periode_classe(item.jour, item.heure_deb, item.heure_fin, item.id_classe, annee.id)
                self._check_enseignant_periode(item.jour, item.heure_deb, item.heure_fin, item.id_enseignant, annee.id)
                cours_dict = item.model_dump()
                cours_dict["id_annee"] = annee.id
                db_cours = Cours.model_validate(cours_dict)
                new_cours = self.cours_repository.save(db_cours)
                new_cours_list.append(new_cours)
            self._session().commit()
            return new_cours_list
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout en masse des cours: {str(e)}")

    def update_cours(self, cours_id: int, data: CoursUpdateDTO) -> CoursResponseDTO:
        """Modifie un cours en BD"""
        try:
            db_cours = self.cours_repository.findOne(cours_id)
            self._check_cours_exists(db_cours)
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_cours, key, value)
            updated = self.cours_repository.save(db_cours)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du cours: {str(e)}")

    def update_bulk_cours(self, data: CoursBulkUpdateDTO) -> list[CoursResponseDTO]:
        """Modifie plusieurs cours en masse en BD"""
        try:
            for item in data.cours:
                db_cours = self.cours_repository.findOne(item.id)
                self._check_cours_exists(db_cours)
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    self.cours_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            return [self.cours_repository.findOne(item.id) for item in data.cours]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification en masse des cours: {str(e)}")

    def get_cours_by_enseignant(self, id_enseignant: int) -> list[CoursParEnseignantResponseDTO]:
        """Récupère les cours d'un enseignant pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            return self.cours_repository.findBy(id_enseignant=id_enseignant, id_annee=annee.id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des cours: {str(e)}")

    def get_cours_by_classe(self, id_classe: int) -> list[CoursParClasseResponseDTO]:
        """Récupère les cours d'une classe pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            return self.cours_repository.findBy(id_classe=id_classe, id_annee=annee.id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des cours: {str(e)}")

    def delete_cours(self, cours_id: int):
        """Supprime un cours en BD"""
        try:
            db_cours = self.cours_repository.findOne(cours_id)
            self._check_cours_exists(db_cours)
            deleted = self.cours_repository.deleteOne(cours_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": cours_id, "message": "Cours supprimé"}}
            return {"success": False, "detail": {"id": cours_id, "message": "Cours non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du cours: {str(e)}")
