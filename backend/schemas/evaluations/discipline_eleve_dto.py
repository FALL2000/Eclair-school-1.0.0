from sqlmodel import Field, SQLModel


class DisciplineEleveBase(SQLModel):
    nb_heure_obtenu: int = Field(
        ge=0,
        description="Nombre d'heures d'absence obtenues(non justifiées)",
        nullable=False,
    )
    nb_heure_justifie: int = Field(
        ge=0,
        description="Nombre d'heures d'absence justifiées",
        nullable=False,
    )
    nb_heure_total: int = Field(
        ge=0,
        description="Nombre total d'heures d'absence total",
        nullable=False,
    )


class DisciplineEleveCreateDTO(DisciplineEleveBase):
    pass


class DisciplineEleveItemCreateDTO(DisciplineEleveBase):
    id_eleve: int


class DisciplineEleveBulkCreateDTO(SQLModel):
    id_classe: int
    id_evaluation: int
    disciplines: list[DisciplineEleveItemCreateDTO]


class DisciplineEleveUpdateDTO(SQLModel):
    nb_heure_obtenu: int | None = Field(default=None, ge=0)
    nb_heure_justifie: int | None = Field(default=None, ge=0)
    nb_heure_total: int | None = Field(default=None, ge=0)


class DisciplineEleveBulkUpdateItemDTO(DisciplineEleveUpdateDTO):
    id: int


class DisciplineEleveBulkUpdateDTO(SQLModel):
    disciplines: list[DisciplineEleveBulkUpdateItemDTO]


class DisciplineEleveResponseDTO(DisciplineEleveBase):
    id: int
    id_eleve: int
    id_annee: int
    id_classe: int
    id_evaluation: int
    id_discipline_decision: int | None = None
