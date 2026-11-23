from fastapi import HTTPException

from models.administration.etablissement import Etablissement
from repositories.administration.etablissement_repository import EtablissementRepository


class EtablissementService:
    def __init__(self, etablissement_repository: EtablissementRepository):
        self.etablissement_repository = etablissement_repository

    def get_etablissement(self) -> Etablissement:
        """Retourne l'etablissement (une seule ligne en BD)"""
        db_etablissement = self.etablissement_repository.find_unique()
        if db_etablissement is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ETABLISSEMENT_NOT_FOUND",
                    "message": "Etablissement non renseigné",
                },
            )
        return db_etablissement
