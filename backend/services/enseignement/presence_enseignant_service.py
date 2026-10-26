from datetime import date
from typing import Optional

from fastapi import HTTPException

from common.permissions import Action, Module, code_permission
from models.enseignement.cours import Cours
from models.enseignement.presence_enseignant import PresenceEnseignant
from repositories.administration.annee_repository import AnneeRepository
from repositories.enseignement.presence_enseignant_repository import PresenceEnseignantRepository
from schemas.enseignement.presence_enseignant_dto import (
    PresenceEnseignantCreateDTO,
    PresenceEnseignantResponseDTO,
    PresenceEnseignantUpdateDTO,
    PresencesJourDTO,
    PresencesJourSaveDTO,
)
from services.administration.annee_service import AnneeService

# Jours de la semaine tels qu'enregistres dans cours.jour (date.weekday() : 0 = lundi)
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


class PresenceEnseignantService:
    def __init__(self, presence_enseignant_repository: PresenceEnseignantRepository,
                 annee_repository: AnneeRepository | None = None):
        self.presence_enseignant_repository = presence_enseignant_repository
        self.annee_repository = annee_repository

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

    @staticmethod
    def _check_date(date_cours: date):
        if date_cours > date.today():
            raise HTTPException(
                status_code=400,
                detail={"error_code": "DATE_FUTURE", "message": "La présence ne peut pas être saisie pour une date future"},
            )

    def _get_cours(self, id_cours: int) -> Cours:
        cours = self.presence_enseignant_repository.get_cours(id_cours)
        if cours is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "COURS_NOT_FOUND", "message": f"Cours {id_cours} non trouvé"},
            )
        return cours

    @staticmethod
    def _check_jour_cours(cours: Cours, date_cours: date):
        """Le cours doit avoir lieu le jour de la semaine de date_cours"""
        if (cours.jour or "").strip().lower() != JOURS_SEMAINE[date_cours.weekday()].lower():
            raise HTTPException(
                status_code=400,
                detail={"error_code": "JOUR_COURS_DIFFERENT",
                        "message": f"Le cours {cours.id} a lieu le {cours.jour}, pas le {JOURS_SEMAINE[date_cours.weekday()].lower()}"},
            )

    def _check_doublon(self, id_cours: int, date_cours: date, exclude_id: int | None = None):
        if self.presence_enseignant_repository.find_presence(id_cours, date_cours, exclude_id) is not None:
            raise HTTPException(
                status_code=409,
                detail={"error_code": "PRESENCE_DEJA_SAISIE", "message": "La présence de ce cours est déjà saisie pour cette date"},
            )

    def add_presence_enseignant(
        self,
        data: PresenceEnseignantCreateDTO,
        id_cours: int,
        id_enseignant: int,
    ) -> PresenceEnseignantResponseDTO:
        """Ajoute une présence enseignant en BD : cours existant, enseignant du cours, date passée
        correspondant au jour du cours, une seule présence par cours et par date"""
        try:
            self._check_date(data.date_cours)
            cours = self._get_cours(id_cours)
            if cours.id_enseignant != id_enseignant:
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "ENSEIGNANT_COURS_DIFFERENT", "message": "Cet enseignant n'assure pas ce cours"},
                )
            self._check_jour_cours(cours, data.date_cours)
            self._check_doublon(id_cours, data.date_cours)
            presence_dict = data.model_dump()
            if presence_dict["is_present"]:
                presence_dict["is_justifie"] = False
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
            if "date_cours" in update_data and update_data["date_cours"] != db_presence.date_cours:
                self._check_date(update_data["date_cours"])
                self._check_jour_cours(self._get_cours(db_presence.id_cours), update_data["date_cours"])
                self._check_doublon(db_presence.id_cours, update_data["date_cours"], exclude_id=db_presence.id)
            for key, value in update_data.items():
                setattr(db_presence, key, value)
            if db_presence.is_present:
                db_presence.is_justifie = False
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

    def get_presences_jour(self, date_cours: date, q: str | None, id_enseignant: int | None,
                           id_classe: int | None = None) -> PresencesJourDTO:
        """Cours planifies a cette date (jour de la semaine, annee en cours), toutes classes ou une classe,
        avec la presence de leur enseignant si elle est deja saisie"""
        try:
            annee = AnneeService(self.annee_repository).get_annee_scolaire()[0]
            jour = JOURS_SEMAINE[date_cours.weekday()]
            termes = [terme for terme in (q or "").split() if terme]
            lignes = self.presence_enseignant_repository.cours_du_jour(
                jour, annee.id, termes, id_enseignant, id_classe)
            presences = self.presence_enseignant_repository.presences_du_jour(date_cours, [c.id for c, *_ in lignes])
            cours = []
            for c, classe, matiere, nom, prenom in lignes:
                p = presences.get(c.id)
                cours.append({
                    "id_cours": c.id, "heure_deb": c.heure_deb, "heure_fin": c.heure_fin,
                    "id_classe": c.id_classe, "classe": classe, "id_matiere": c.id_matiere, "matiere": matiere,
                    "id_enseignant": c.id_enseignant, "nom": nom, "prenom": prenom,
                    "id_presence": p.id if p else None,
                    "is_present": p.is_present if p else None,
                    "is_justifie": p.is_justifie if p else None,
                })
            return PresencesJourDTO(
                date_cours=date_cours,
                jour=jour,
                nb_saisies=sum(1 for c in cours if c["id_presence"] is not None),
                nb_absents=sum(1 for c in cours if c["is_present"] is False),
                cours=cours,
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des présences du jour: {str(e)}")

    def enregistrer_presences_jour(self, data: PresencesJourSaveDTO, current_user: dict) -> PresencesJourDTO:
        """Enregistre en une fois la presence des enseignants pour les cours d'une date.
        Une presence deja saisie est mise a jour (permission presence_enseignant:modifier)"""
        try:
            self._check_date(data.date_cours)
            ids = [p.id_cours for p in data.presences]
            if len(ids) != len(set(ids)):
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "COURS_DUPLIQUE", "message": "Un même cours apparaît plusieurs fois dans la liste"},
                )
            peut_modifier = current_user.get("is_super_admin", False) or code_permission(
                Module.PRESENCE_ENSEIGNANT, Action.MODIFIER) in current_user.get("permissions", [])
            existantes = self.presence_enseignant_repository.presences_du_jour(data.date_cours, ids)
            for saisie in data.presences:
                cours = self._get_cours(saisie.id_cours)
                self._check_jour_cours(cours, data.date_cours)
                is_justifie = saisie.is_justifie and not saisie.is_present
                presence = existantes.get(cours.id)
                if presence is None:
                    presence = PresenceEnseignant(
                        id_cours=cours.id, id_enseignant=cours.id_enseignant, date_cours=data.date_cours,
                        is_present=saisie.is_present, is_justifie=is_justifie)
                elif (presence.is_present, presence.is_justifie) != (saisie.is_present, is_justifie):
                    if not peut_modifier:
                        raise HTTPException(
                            status_code=403,
                            detail={"error_code": "PERMISSION_REFUSEE",
                                    "message": "Modifier une présence déjà saisie nécessite presence_enseignant:modifier"},
                        )
                    presence.is_present, presence.is_justifie = saisie.is_present, is_justifie
                else:
                    continue
                self.presence_enseignant_repository.save(presence)
            self._session().commit()
            return self.get_presences_jour(data.date_cours, None, None)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'enregistrement des présences: {str(e)}")
