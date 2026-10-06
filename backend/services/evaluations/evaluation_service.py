from datetime import date

from fastapi import HTTPException

from models.evaluations.evaluation import Evaluation
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from schemas.evaluations.evaluation_dto import EvaluationCreateDTO, EvaluationUpdateDTO


class EvaluationService:
    def __init__(self, evaluation_repository: EvaluationRepository, trimestre_repository: TrimestreRepository):
        self.evaluation_repository = evaluation_repository
        self.trimestre_repository = trimestre_repository

    def _session(self):
        return self.evaluation_repository.session

    def _check_code_exists(self, code: str):
        exist_evaluation = self.evaluation_repository.findByCode(code)
        if len(exist_evaluation) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L'évaluation avec le code {code} existe déjà."
                }
            )

    def _check_evaluation_exists(self, db_evaluation: Evaluation | None):
        if db_evaluation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "EVALUATION_NOT_FOUND",
                    "message": "Évaluation non trouvée"
                }
            )

    def _check_trimestre_exists(self, id_trimestre: int):
        if self.trimestre_repository.findOne(id_trimestre, load_relations=False) is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "TRIMESTRE_NOT_FOUND",
                    "message": "Trimestre non trouvé"
                }
            )

    def _check_dates(self, date_deb: date, date_fin: date):
        if date_deb > date_fin:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_DATES",
                    "message": "La date de début doit être antérieure ou égale à la date de fin"
                }
            )

    def add_evaluation(self, evaluation_in: EvaluationCreateDTO, id_trimestre: int):
        """Ajoute une évaluation en BD"""
        try:
            self._check_trimestre_exists(id_trimestre)
            self._check_code_exists(evaluation_in.code)
            self._check_dates(evaluation_in.date_deb, evaluation_in.date_fin)
            evaluation_dict = evaluation_in.model_dump()
            evaluation_dict["id_trimestre"] = id_trimestre
            db_evaluation = Evaluation.model_validate(evaluation_dict)
            new_evaluation = self.evaluation_repository.save(db_evaluation)
            self._session().commit()
            return new_evaluation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de l'évaluation: {str(e)}")

    def update_evaluation(self, evaluation_id: int, evaluation_update: EvaluationUpdateDTO):
        """Modifie une évaluation en BD"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id)
            self._check_evaluation_exists(db_evaluation)
            if evaluation_update.code is not None and evaluation_update.code != db_evaluation.code:
                self._check_code_exists(evaluation_update.code)
            if evaluation_update.id_trimestre is not None and evaluation_update.id_trimestre != db_evaluation.id_trimestre:
                self._check_trimestre_exists(evaluation_update.id_trimestre)
            self._check_dates(
                evaluation_update.date_deb or db_evaluation.date_deb,
                evaluation_update.date_fin or db_evaluation.date_fin,
            )
            update_data = evaluation_update.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(db_evaluation, key, value)
            updated = self.evaluation_repository.save(db_evaluation)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'évaluation: {str(e)}")

    def delete_evaluation(self, evaluation_id: int):
        """Supprime une évaluation en BD — impossible si des notes ou disciplines y sont rattachées"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id)
            self._check_evaluation_exists(db_evaluation)
            if len(db_evaluation.notations) > 0 or len(db_evaluation.disciplines) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une évaluation à laquelle des notes ou disciplines sont rattachées"
                    }
                )
            deleted = self.evaluation_repository.deleteOne(evaluation_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": evaluation_id, "message": "Évaluation supprimée"}
                }
            return {
                "success": False,
                "detail": {"id": evaluation_id, "message": "Évaluation non supprimée"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'évaluation: {str(e)}")

    def get_one_evaluation(self, evaluation_id: int):
        """Récupère une évaluation en BD"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id)
            self._check_evaluation_exists(db_evaluation)
            return db_evaluation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de l'évaluation: {str(e)}")

    def get_all_evaluations(self, id_trimestre: int | None = None):
        """Récupère toutes les évaluations en BD, éventuellement filtrées par trimestre"""
        try:
            if id_trimestre is not None:
                return self.evaluation_repository.findBy(load_relations=False, id_trimestre=id_trimestre)
            return self.evaluation_repository.findAll(load_relations=False)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des évaluations: {str(e)}")
