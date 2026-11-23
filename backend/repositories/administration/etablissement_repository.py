from typing import Optional

from sqlmodel import Session, select

from models.administration.etablissement import Etablissement
from repositories.base_repository import BaseRepository


class EtablissementRepository(BaseRepository[Etablissement]):

    def __init__(self, session: Session):
        super().__init__(Etablissement, session)

    def find_unique(self) -> Optional[Etablissement]:
        """La table ne contient qu'une ligne : l'etablissement de l'application"""
        return self.session.exec(select(Etablissement).order_by(Etablissement.id)).first()
