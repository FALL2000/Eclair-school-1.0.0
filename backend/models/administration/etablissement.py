from typing import Optional

from sqlmodel import Field

from schemas.administration.etablissement_dto import EtablissementBase


class Etablissement(EtablissementBase, table=True):
    __tablename__ = "etablissement"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'etablissement")
