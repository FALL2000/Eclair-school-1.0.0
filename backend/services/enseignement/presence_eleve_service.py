from datetime import date
from typing import Optional

from fastapi import HTTPException

from models.enseignement.presence_eleve import PresenceEleve
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.enseignement.presence_eleve_repository import PresenceEleveRepository
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_eleve_dto import (
    PresenceEleveBulkCreateDTO,
    PresenceEleveBulkUpdateDTO,
    PresenceEleveResponseDTO,
    PresenceEleveWithEleveResponseDTO,
)


class PresenceEleveService:
    def __init__(
        self,
        presence_eleve_repository: PresenceEleveRepository,
        presence_enseignant_repository: PresenceEnseignantRepository,
        configuration_repository: ConfigurationRepository,
    ):
        self.presence_eleve_repository = presence_eleve_repository
        self.presence_enseignant_repository = presence_enseignant_repository
        self.configuration_repository = configuration_repository

    def _session(self):
        return self.presence_eleve_repository.session

    def _check_presence_exists(self, db_presence: PresenceEleve | None):
        if db_presence is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "PRESENCE_ELEVE_NOT_FOUND",
                    "message": "Présence élève non trouvée",
                },
            )

    def _check_appel_actif(self):
        configurations = self.configuration_repository.findAll()
        if not configurations:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "CONFIGURATION_NOT_FOUND",
                    "message": "Configuration non trouvée",
                },
            )
        if not configurations[0].is_appel:
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "APPEL_NOT_ACTIVE",
                    "message": "L'appel n'est pas activé dans la configuration",
                },
            )

    def get_presences_by_filters(
        self,
        id_cours: Optional[int] = None,
        date_cours: Optional[date] = None,
    ) -> list[PresenceEleveWithEleveResponseDTO]:
        """Récupère les présences élèves filtrées par cours et/ou date, avec les infos élève"""
        try:
            filters = {}
            if id_cours is not None:
                filters["id_cours"] = id_cours
            if date_cours is not None:
                filters["date_cours"] = date_cours
            return self.presence_eleve_repository.findBy(**filters)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des présences élèves: {str(e)}",
            )

    def add_bulk_presences_eleves(
        self, data: PresenceEleveBulkCreateDTO
    ) -> list[PresenceEleveResponseDTO]:
        """Ajoute en masse les présences des élèves si l'appel est actif dans la configuration."""
        try:
            self._check_appel_actif()
            data_list = [
                {
                    "id_cours": data.id_cours,
                    "id_eleve": item.id_eleve,
                    "date_cours": data.date_cours,
                    "is_present": item.is_present,
                    "is_justifie": item.is_justifie,
                }
                for item in data.presences
            ]
            self.presence_eleve_repository.InsertMany(data_list)
            self._session().commit()
            return self.presence_eleve_repository.findBy(
                id_cours=data.id_cours, date_cours=data.date_cours
            )
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de l'ajout en masse des présences élèves: {str(e)}",
            )

    def update_bulk_presences_eleves(
        self, data: PresenceEleveBulkUpdateDTO
    ) -> list[PresenceEleveResponseDTO]:
        """Modifie en masse les présences des élèves"""
        try:
            for item in data.presences:
                db_presence = self.presence_eleve_repository.findOne(item.id)
                self._check_presence_exists(db_presence)
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    self.presence_eleve_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            return [
                self.presence_eleve_repository.findOne(item.id) for item in data.presences
            ]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la modification en masse des présences élèves: {str(e)}",
            )
