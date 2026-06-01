from typing import Optional

from sqlmodel import Field

from schemas.administration.configuration_dto import ConfigurationBase


class Configuration(ConfigurationBase, table=True):
    __tablename__ = "configuration"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la configuration"
    )
