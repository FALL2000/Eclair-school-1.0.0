from fastapi import HTTPException

from models.administration.discipline_decision import DisciplineDecision
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from schemas.administration.discipline_decision_dto import (
    DisciplineDecisionCreateDTO,
    DisciplineDecisionUpdateDTO,
)


class DisciplineDecisionService:
    def __init__(
        self,
        discipline_decision_repository: DisciplineDecisionRepository,
        annee_repository: AnneeRepository,
    ):
        self.discipline_decision_repository = discipline_decision_repository
        self.annee_repository = annee_repository

    def _session(self):
        return self.discipline_decision_repository.session

    def _check_non_attribuee_annee_en_cours(self, db_decision: DisciplineDecision, action: str):
        """Empêche la modification ou la suppression d'une décision déjà attribuée
        à des élèves pendant l'année scolaire en cours"""
        ids_annees_en_cours = {a.id for a in self.annee_repository.findByIs_cloture(False)}
        if any(d.id_annee in ids_annees_en_cours for d in db_decision.disciplines_eleves):
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DECISION_ATTRIBUEE",
                    "message": f"Impossible de {action} une décision disciplinaire déjà attribuée à des élèves pendant l'année scolaire en cours"
                }
            )

    def _check_libelle_exists(self, libelle: str):
        exist_decision = self.discipline_decision_repository.findByLibelle(libelle)
        if len(exist_decision) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_LIBELLE",
                    "message": f"La décision disciplinaire avec le libellé {libelle} existe déjà."
                }
            )

    def _check_decision_exists(self, db_decision: DisciplineDecision | None):
        if db_decision is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "DISCIPLINE_DECISION_NOT_FOUND",
                    "message": "Décision disciplinaire non trouvée"
                }
            )

    def _check_intervalle(self, nb_heure_min: int, nb_heure_max: int, decision_id: int | None = None):
        if nb_heure_min > nb_heure_max:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INTERVALLE_INVALIDE",
                    "message": "Le nombre minimal d'heures doit être inférieur ou égal au nombre maximal"
                }
            )
        chevauchements = [
            d for d in self.discipline_decision_repository.find_chevauchement(nb_heure_min, nb_heure_max)
            if d.id != decision_id
        ]
        if len(chevauchements) > 0:
            decision = chevauchements[0]
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "INTERVALLE_CHEVAUCHEMENT",
                    "message": (
                        f"L'intervalle [{nb_heure_min}, {nb_heure_max}] chevauche celui de la décision "
                        f"{decision.libelle} [{decision.nb_heure_min}, {decision.nb_heure_max}]"
                    )
                }
            )

    def add_decision(self, decision_in: DisciplineDecisionCreateDTO):
        """Ajoute une décision disciplinaire en BD"""
        try:
            self._check_libelle_exists(decision_in.libelle)
            self._check_intervalle(decision_in.nb_heure_min, decision_in.nb_heure_max)
            db_decision = DisciplineDecision.model_validate(decision_in)
            new_decision = self.discipline_decision_repository.save(db_decision)
            self._session().commit()
            return new_decision
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la décision disciplinaire: {str(e)}")

    def update_decision(self, decision_update: DisciplineDecisionUpdateDTO, decision_id: int):
        """Modifie une décision disciplinaire en BD"""
        try:
            db_decision = self.discipline_decision_repository.findOne(decision_id)
            self._check_decision_exists(db_decision)
            self._check_non_attribuee_annee_en_cours(db_decision, "modifier")
            if decision_update.libelle is not None and decision_update.libelle != db_decision.libelle:
                self._check_libelle_exists(decision_update.libelle)
            update_data = decision_update.model_dump(exclude_unset=True, exclude_none=True)
            self._check_intervalle(
                update_data.get("nb_heure_min", db_decision.nb_heure_min),
                update_data.get("nb_heure_max", db_decision.nb_heure_max),
                decision_id,
            )
            for key, value in update_data.items():
                setattr(db_decision, key, value)
            new_decision = self.discipline_decision_repository.save(db_decision)
            self._session().commit()
            return new_decision
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la décision disciplinaire: {str(e)}")

    def delete_decision(self, decision_id: int):
        """Supprime une décision disciplinaire en BD"""
        try:
            db_decision = self.discipline_decision_repository.findOne(decision_id)
            self._check_decision_exists(db_decision)
            self._check_non_attribuee_annee_en_cours(db_decision, "supprimer")
            if len(db_decision.disciplines_eleves) > 0:
                # Attribuée lors d'années précédentes : la clé étrangère empêche la suppression
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une décision disciplinaire attribuée à des élèves lors d'années précédentes"
                    }
                )
            deleted =self.discipline_decision_repository.deleteOne(decision_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": decision_id, "message": "Décision disciplinaire supprimée"}
                }
            return {
                "success": False,
                "detail": {"id": decision_id, "message": "Décision disciplinaire non supprimée"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la décision disciplinaire: {str(e)}")

    def get_one_decision(self, decision_id: int):
        """Récupère une décision disciplinaire en BD"""
        try:
            db_decision = self.discipline_decision_repository.findOne(decision_id)
            self._check_decision_exists(db_decision)
            return db_decision
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de la décision disciplinaire: {str(e)}")

    def get_all_decisions(self):
        """Récupère toutes les décisions disciplinaires en BD"""
        try:
            return self.discipline_decision_repository.findAll()
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des décisions disciplinaires: {str(e)}")
