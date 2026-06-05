from datetime import date
from typing import Optional

from fastapi import HTTPException

from models.enseignement.presence_enseignant import PresenceEnseignant
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_enseignant_dto import (
    PresenceEnseignantCreateDTO,
    PresenceEnseignantResponseDTO,
    PresenceEnseignantUpdateDTO,
)


class PresenceEnseignantService:
    def __init__(self, presence_enseignant_repository: PresenceEnseignantRepository):
        self.presence_enseignant_repository = presence_enseignant_repository

    def _session(self):
        return self.presence_enseignant_repository.session

    def _check_presence_exists(self, db_presence: PresenceEnseignant | None):
        if db_presence is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "PRESENCE_ENSEIGNANT_NOT_FOUND",
                    "message": "Présence enseignant non trouvée",
                },
            )

    def add_presence_enseignant(
        self,
        data: PresenceEnseignantCreateDTO,
        id_cours: int,
        id_enseignant: int,
    ) -> PresenceEnseignantResponseDTO:
        """Ajoute une présence enseignant en BD"""
        try:
            presence_dict = data.model_dump()
            presence_dict["id_cours"] = id_cours
            presence_dict["id_enseignant"] = id_enseignant
            db_presence = PresenceEnseignant.model_validate(presence_dict)
            new_presence = self.presence_enseignant_repository.save(db_presence)
            self._session().commit()
            return new_presence
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de l'ajout de la présence enseignant: {str(e)}",
            )

    def get_presences_by_filters(
        self,
        id_cours: Optional[int] = None,
        date_cours: Optional[date] = None,
    ) -> list[PresenceEnseignantResponseDTO]:
        """Récupère les présences enseignants filtrées par cours et/ou date"""
        try:
            filters = {}
            if id_cours is not None:
                filters["id_cours"] = id_cours
            if date_cours is not None:
                filters["date_cours"] = date_cours
            return self.presence_enseignant_repository.findBy(**filters)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des présences enseignants: {str(e)}",
            )

    def update_presence_enseignant(
        self,
        presence_id: int,
        data: PresenceEnseignantUpdateDTO,
    ) -> PresenceEnseignantResponseDTO:
        """Modifie une présence enseignant en BD"""
        try:
            db_presence = self.presence_enseignant_repository.findOne(presence_id)
            self._check_presence_exists(db_presence)
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_presence, key, value)
            updated = self.presence_enseignant_repository.save(db_presence)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la modification de la présence enseignant: {str(e)}",
            )
