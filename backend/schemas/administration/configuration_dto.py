from typing import Optional

from sqlmodel import Field, SQLModel


class ConfigurationBase(SQLModel):
    is_appel: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'appel est activé",
    )
    is_absence_justifiee_payee: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "0"},
        description="Salaire horaire : les absences justifiees des enseignants sont payees comme des heures de presence",
    )
    is_discipline_manage: bool = Field(
        default=True,
        nullable=False,
        sa_column_kwargs={"server_default": "1"},
        description="Indique si l'etablissement gere la discipline (appel des eleves, disciplines, partie discipline "
                    "du bulletin). Seul le primaire peut la desactiver",
    )


class ConfigurationCreateDTO(ConfigurationBase):
    pass


class ConfigurationUpdateDTO(SQLModel):
    is_appel: Optional[bool] = None
    is_absence_justifiee_payee: Optional[bool] = None
    is_discipline_manage: Optional[bool] = None


class ConfigurationResponseDTO(ConfigurationBase):
    id: int
