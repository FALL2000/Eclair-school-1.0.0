from fastapi import HTTPException

from common.enumeration import TYPE_NOTATION_PAR_TYPE_SCHOOL, TypeNotation
from config.settings import get_settings
from models.administration.configuration import Configuration
from repositories.administration.configuration_repository import ConfigurationRepository
from schemas.administration.configuration_dto import ConfigurationCreateDTO, ConfigurationUpdateDTO


class ConfigurationService:
    def __init__(self, configuration_repository: ConfigurationRepository):
        self.configuration_repository = configuration_repository

    def _session(self):
        return self.configuration_repository.session

    def _check_configuration_exists(self, db_configuration: Configuration | None):
        if db_configuration is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "CONFIGURATION_NOT_FOUND",
                    "message": "Configuration non trouvée",
                },
            )

    def add_configuration(self, configuration_in: ConfigurationCreateDTO):
        """Ajoute une configuration en BD"""
        try:
            db_configuration = Configuration.model_validate(configuration_in)
            self._appliquer_regles_discipline(db_configuration, configuration_in.is_appel)
            new_configuration = self.configuration_repository.save(db_configuration)
            self._session().commit()
            return new_configuration
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la configuration: {str(e)}")

    def _appliquer_regles_discipline(self, db_configuration: Configuration, appel_demande: bool):
        """Seul le primaire peut ne pas gerer la discipline ; sans discipline, pas d'appel des eleves"""
        if db_configuration.is_discipline_manage:
            return
        type_school = get_settings().type_school.strip().lower()
        if TYPE_NOTATION_PAR_TYPE_SCHOOL.get(type_school) != TypeNotation.PRIMAIRE:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DISCIPLINE_OBLIGATOIRE",
                    "message": "Seul un établissement primaire peut désactiver la gestion de la discipline",
                },
            )
        if db_configuration.is_appel and appel_demande:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "APPEL_SANS_DISCIPLINE",
                    "message": "L'appel des élèves ne peut pas être activé quand la discipline n'est pas gérée",
                },
            )
        db_configuration.is_appel = False

    def update_configuration(self, configuration_id: int, configuration_update: ConfigurationUpdateDTO):
        """Modifie une configuration en BD"""
        try:
            db_configuration = self.configuration_repository.findOne(configuration_id)
            self._check_configuration_exists(db_configuration)
            update_data = configuration_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_configuration, key, value)
            self._appliquer_regles_discipline(db_configuration, update_data.get("is_appel") is True)
            updated = self.configuration_repository.save(db_configuration)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la configuration: {str(e)}")
