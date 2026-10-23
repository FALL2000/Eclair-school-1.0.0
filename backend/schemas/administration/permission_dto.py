from sqlmodel import Field, SQLModel


class PermissionBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=100,
        description="Code unique de la permission : module:action (ex: eleve:inscrire)",
        nullable=False,
    )
    module: str = Field(
        max_length=50,
        description="Module concerné (ex: eleve, reglement, classe)",
        nullable=False,
    )
    action: str = Field(
        max_length=30,
        description="Action autorisée (ajouter, modifier, supprimer, consulter, rechercher, inscrire, annuler, ...)",
        nullable=False,
    )
    domaine: str = Field(
        max_length=30,
        description="Domaine fonctionnel (administration, securite, eleves, enseignement, evaluations, scolarite)",
        nullable=False,
    )
    libelle: str = Field(
        max_length=150,
        description="Libellé lisible de la permission (ex: Inscrire un élève)",
        nullable=False,
    )


class PermissionResponseDTO(PermissionBase):
    id: int
