from sqlmodel import Field, SQLModel


class DisciplineEleveBase(SQLModel):
    nb_heure_obtenu: int = Field(
        description="Nombre d'heures d'absence obtenues",
        nullable=False,
    )
    nb_heure_justifie: int = Field(
        description="Nombre d'heures d'absence justifiées",
        nullable=False,
    )
    nb_heure_total: int = Field(
        description="Nombre total d'heures d'absence total",
        nullable=False,
    )


class DisciplineEleveCreateDTO(DisciplineEleveBase):
    pass


class DisciplineEleveUpdateDTO(SQLModel):
    nb_heure_obtenu: int | None = None
    nb_heure_justifie: int | None = None
    nb_heure_total: int | None = None


class DisciplineEleveResponseDTO(DisciplineEleveBase):
    id: int
