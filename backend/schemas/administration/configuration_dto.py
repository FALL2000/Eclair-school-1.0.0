from typing import Optional

from sqlmodel import Field, SQLModel


class ConfigurationBase(SQLModel):
    is_appel: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'appel est activé",
    )


class ConfigurationCreateDTO(ConfigurationBase):
    pass


class ConfigurationUpdateDTO(SQLModel):
    is_appel: Optional[bool] = None


class ConfigurationResponseDTO(ConfigurationBase):
    id: int
