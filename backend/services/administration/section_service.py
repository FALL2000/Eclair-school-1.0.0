from fastapi import HTTPException

from repositories.administration.annee_repository import AnneeRepository
from models.administration.section import Section
from schemas.administration.section_dto import SectionCreateDTO, SectionUpdateDTO
from repositories.administration.section_repository import SectionRepository


class SectionService:
    def __init__(self, section_repository: SectionRepository, annee_repository: AnneeRepository):
        self.section_repository = section_repository
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_section = self.section_repository.findByCode(code)
        if len(exist_section) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"La section avec le code {code} existe déjà."
                }
            )

    def _check_section_exists(self, db_section: Section | None):
        if db_section is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "SECTION_NOT_FOUND",
                    "message": "section non trouve"
                }
            )

    def add_section(self, section_in: SectionCreateDTO):
        """Ajoute une section en BD"""
        try:
            self._check_code_exists(section_in.code)
            db_section = Section.model_validate(section_in)
            new_section = self.section_repository.save(db_section)
            self.section_repository.session.commit()
            return new_section
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.section_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la section: {str(e)}")

    def update_section(self, section_update: SectionUpdateDTO, section_id: int):
        """Modifie une section BD"""
        try:
            db_section = self.section_repository.findOne(section_id)
            self._check_section_exists(db_section)
            if section_update.code is not None and section_update.code != db_section.code:
                self._check_code_exists(section_update.code)
            update_data = section_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_section, key, value)
            new_section = self.section_repository.save(db_section)
            self.section_repository.session.commit()
            return new_section
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.section_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification  de la section: {str(e)}")

    def delete_section(self, section_id: int):
        """Supprime une section en BD"""
        try:
            db_section = self.section_repository.findOne(section_id)
            self._check_section_exists(db_section)
            if self.annee_repository.findByIs_cloture(False) is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une section durant une annee scolaire en cours"
                    }
                )
            delete_section = self.section_repository.deleteOne(section_id)
            if delete_section:
                return {
                    "success": True,
                    "detail": {"id": section_id, "message": "Section supprimée"}
                }
            else:
                return {
                    "success": False,
                    "detail": {"id": section_id, "message": "Section non supprimée"}
                }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.section_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression  de la section: {str(e)}")

    def get_one_section(self, section_id: int):
        """Recupere une section en BD"""
        try:
            db_section = self.section_repository.findOne(section_id)
            self._check_section_exists(db_section)
            return db_section
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.section_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation  de la section: {str(e)}")

    def get_all_section(self):
        """Recupere toutes les sections en BD"""
        try:
            db_sections = self.section_repository.findAll()
            return db_sections
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.section_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation  des sections: {str(e)}")
