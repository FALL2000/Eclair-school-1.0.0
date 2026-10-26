from datetime import time
from typing import Optional

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

    def _check_heures(self, heure_deb: time, heure_fin: time):
        if heure_deb >= heure_fin:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "HEURES_INVALIDES",
                    "message": "L'heure de début doit être strictement inférieure à l'heure de fin",
                },
            )

    def _check_periode_classe(
        self, jour: str, heure_deb: time, heure_fin: time, id_classe: int, id_annee: int,
        exclude_id: int | None = None,
    ):
        existing = self.cours_repository.find_chevauchement(
            jour=jour, heure_deb=heure_deb, heure_fin=heure_fin,
            id_annee=id_annee, id_classe=id_classe, exclude_id=exclude_id,
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "COURS_PERIODE_CLASSE_CONFLICT",
                    "message": "Un cours existe déjà à cette période dans cette classe",
                },
            )

    def _check_enseignant_periode(
        self, jour: str, heure_deb: time, heure_fin: time, id_enseignant: int, id_annee: int,
        exclude_id: int | None = None,
    ):
        existing = self.cours_repository.find_chevauchement(
            jour=jour, heure_deb=heure_deb, heure_fin=heure_fin,
            id_annee=id_annee, id_enseignant=id_enseignant, exclude_id=exclude_id,
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "ENSEIGNANT_PERIODE_CONFLICT",
                    "message": "L'enseignant a déjà un cours à cette période dans une autre classe",
                },
            )

    def _check_enseignant_matiere(self, id_enseignant: int, id_matiere: int):
        """L'enseignant doit exister, etre actif et enseigner la matiere du cours"""
        enseignant = self.cours_repository.get_enseignant(id_enseignant)
        if enseignant is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "ENSEIGNANT_NOT_FOUND", "message": "Enseignant non trouvé"},
            )
        if not enseignant.is_active:
            raise HTTPException(
                status_code=409,
                detail={"error_code": "ENSEIGNANT_INACTIF", "message": "Impossible de planifier un cours pour un enseignant inactif"},
            )
        if not self.cours_repository.enseigne_matiere(id_enseignant, id_matiere):
            raise HTTPException(
                status_code=400,
                detail={"error_code": "MATIERE_NON_ENSEIGNEE", "message": "Cette matière n'est pas attribuée à l'enseignant"},
            )

    def _check_modification_cours(self, db_cours: Cours, update_data: dict):
        """Vérifie les heures et les conflits de période d'un cours après application des modifications"""
        jour = update_data.get("jour", db_cours.jour)
        heure_deb = update_data.get("heure_deb", db_cours.heure_deb)
        heure_fin = update_data.get("heure_fin", db_cours.heure_fin)
        self._check_heures(heure_deb, heure_fin)
        if (jour, heure_deb, heure_fin) != (db_cours.jour, db_cours.heure_deb, db_cours.heure_fin):
            self._check_periode_classe(
                jour, heure_deb, heure_fin, db_cours.id_classe, db_cours.id_annee, exclude_id=db_cours.id)
            self._check_enseignant_periode(
                jour, heure_deb, heure_fin, db_cours.id_enseignant, db_cours.id_annee, exclude_id=db_cours.id)

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
            self._check_heures(data.heure_deb, data.heure_fin)
            self._check_enseignant_matiere(id_enseignant, id_matiere)
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
                self._check_heures(item.heure_deb, item.heure_fin)
                self._check_enseignant_matiere(item.id_enseignant, item.id_matiere)
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
            update_data = data.model_dump(exclude_unset=True, exclude_none=True)
            self._check_modification_cours(db_cours, update_data)
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
                update_data = item.model_dump(exclude_unset=True, exclude_none=True, exclude={"id"})
                if update_data:
                    self._check_modification_cours(db_cours, update_data)
                    self.cours_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            return [self.cours_repository.findOne(item.id, load_relations=False) for item in data.cours]
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
            return self.cours_repository.findBy(load_relations=True, id_enseignant=id_enseignant, id_annee=annee.id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des cours: {str(e)}")

    def get_cours_by_classe(self, id_classe: int, jour: Optional[str] = None) -> list[CoursParClasseResponseDTO]:
        """Récupère les cours d'une classe pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            filters = {"id_classe": id_classe, "id_annee": annee.id}
            if jour is not None:
                filters["jour"] = jour
            return self.cours_repository.findBy(load_relations=True, **filters)
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
