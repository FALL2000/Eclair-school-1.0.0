from fastapi import HTTPException

from models.enseignants.enseignant import Enseignant
from models.enseignement.enseignement import Enseignement
from repositories.enseignants.enseignant_repository import EnseignantRepository
from repositories.enseignement.enseignement_repository import EnseignementRepository
from schemas.enseignement.enseignement_dto import (
    EnseignantAvecEnseignementsBulkCreateDTO,
    EnseignantAvecEnseignementsResponseDTO,
    EnseignementAvecEnseignantCreateDTO,
    EnseignementAvecEnseignantResponseDTO,
    EnseignementBulkDeleteDTO,
    EnseignementBulkUpdateDTO,
    EnseignementResponseDTO,
    EnseignementSansEnseignantBulkCreateDTO,
    EnseignementUpdateDTO,
)


class EnseignementService:
    def __init__(
        self,
        enseignement_repository: EnseignementRepository,
        enseignant_repository: EnseignantRepository,
    ):
        self.enseignement_repository = enseignement_repository
        self.enseignant_repository = enseignant_repository

    def _session(self):
        return self.enseignement_repository.session

    def _check_enseignement_exists(self, db_enseignement: Enseignement | None):
        if db_enseignement is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ENSEIGNEMENT_NOT_FOUND",
                    "message": "Enseignement non trouvé",
                },
            )

    def _check_duplicate_enseignant_matiere(self, id_enseignant: int, id_matiere: int):
        existing = self.enseignement_repository.findBy(
            id_enseignant=id_enseignant, id_matiere=id_matiere
        )
        if len(existing) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_ENSEIGNANT_MATIERE",
                    "message": f"Un enseignement existe déjà pour cet enseignant et cette matière.",
                },
            )

    def add_enseignement(
        self,
        data: EnseignementAvecEnseignantCreateDTO,
        id_type_salaire: int,
        id_matiere: int,
    ) -> EnseignementAvecEnseignantResponseDTO:
        """Crée un enseignant puis son enseignement"""
        try:
            enseignant_dict = data.enseignant.model_dump()
            enseignant_dict["id_type_salaire"] = id_type_salaire
            db_enseignant = Enseignant.model_validate(enseignant_dict)
            new_enseignant = self.enseignant_repository.save(db_enseignant)

            self._check_duplicate_enseignant_matiere(new_enseignant.id, id_matiere)

            enseignement_dict = data.enseignement.model_dump()
            enseignement_dict["id_enseignant"] = new_enseignant.id
            enseignement_dict["id_matiere"] = id_matiere
            db_enseignement = Enseignement.model_validate(enseignement_dict)
            new_enseignement = self.enseignement_repository.save(db_enseignement)

            self._session().commit()
            return EnseignementAvecEnseignantResponseDTO(
                enseignant=new_enseignant,
                enseignement=new_enseignement,
            )
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de l'enseignement: {str(e)}")

    def add_bulk_with_enseignant(
        self,
        data: EnseignantAvecEnseignementsBulkCreateDTO,
        id_type_salaire: int,
    ) -> EnseignantAvecEnseignementsResponseDTO:
        """Crée un enseignant et plusieurs de ses enseignements en masse"""
        try:
            matieres = [item.id_matiere for item in data.enseignements]
            if len(matieres) != len(set(matieres)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_MATIERE_IN_REQUEST",
                        "message": "Des matières dupliquées sont présentes dans la liste",
                    },
                )

            enseignant_dict = data.enseignant.model_dump()
            enseignant_dict["id_type_salaire"] = id_type_salaire
            db_enseignant = Enseignant.model_validate(enseignant_dict)
            new_enseignant = self.enseignant_repository.save(db_enseignant)

            new_enseignements = []
            for item in data.enseignements:
                self._check_duplicate_enseignant_matiere(new_enseignant.id, item.id_matiere)
                enseignement_dict = item.model_dump()
                enseignement_dict["id_enseignant"] = new_enseignant.id
                db_enseignement = Enseignement.model_validate(enseignement_dict)
                new_enseignement = self.enseignement_repository.save(db_enseignement)
                new_enseignements.append(new_enseignement)

            self._session().commit()
            return EnseignantAvecEnseignementsResponseDTO(
                enseignant=new_enseignant,
                enseignements=new_enseignements,
            )
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout en masse des enseignements: {str(e)}")

    def add_bulk_without_enseignant(
        self,
        data: EnseignementSansEnseignantBulkCreateDTO,
        id_enseignant: int,
    ) -> list[EnseignementResponseDTO]:
        """Crée plusieurs enseignements en masse pour un enseignant existant"""
        try:
            matieres = [item.id_matiere for item in data.items]
            if len(matieres) != len(set(matieres)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_MATIERE_IN_REQUEST",
                        "message": "Des matières dupliquées sont présentes dans la liste",
                    },
                )
            for item in data.items:
                self._check_duplicate_enseignant_matiere(id_enseignant, item.id_matiere)

            data_list = [
                {**item.model_dump(), "id_enseignant": id_enseignant}
                for item in data.items
            ]
            self.enseignement_repository.InsertMany(data_list)
            self._session().commit()
            return self.enseignement_repository.findBy(id_enseignant=id_enseignant)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout en masse des enseignements: {str(e)}")

    def update_enseignement(
        self, enseignement_id: int, data: EnseignementUpdateDTO
    ) -> EnseignementResponseDTO:
        """Modifie un enseignement en BD"""
        try:
            db_enseignement = self.enseignement_repository.findOne(enseignement_id)
            self._check_enseignement_exists(db_enseignement)
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_enseignement, key, value)
            updated = self.enseignement_repository.save(db_enseignement)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'enseignement: {str(e)}")

    def update_bulk_enseignements(
        self, data: EnseignementBulkUpdateDTO
    ) -> list[EnseignementResponseDTO]:
        """Modifie plusieurs enseignements en masse en BD"""
        try:
            for item in data.enseignements:
                db_enseignement = self.enseignement_repository.findOne(item.id)
                self._check_enseignement_exists(db_enseignement)
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    self.enseignement_repository.updateMany({"id": item.id}, update_data)
            self._session().commit()
            return [self.enseignement_repository.findOne(item.id) for item in data.enseignements]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification en masse des enseignements: {str(e)}")

    def delete_enseignement(self, enseignement_id: int):
        """Supprime un enseignement en BD"""
        try:
            db_enseignement = self.enseignement_repository.findOne(enseignement_id)
            self._check_enseignement_exists(db_enseignement)
            deleted = self.enseignement_repository.deleteOne(enseignement_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": enseignement_id, "message": "Enseignement supprimé"}}
            return {"success": False, "detail": {"id": enseignement_id, "message": "Enseignement non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'enseignement: {str(e)}")

    def delete_bulk_enseignements(self, data: EnseignementBulkDeleteDTO):
        """Supprime plusieurs enseignements en masse en BD"""
        try:
            count = self.enseignement_repository.deleteMany(data.ids)
            self._session().commit()
            return {"deleted": count, "message": f"{count} enseignement(s) supprimé(s)"}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression en masse des enseignements: {str(e)}")
