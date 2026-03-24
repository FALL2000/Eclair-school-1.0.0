from sqlmodel import Field, SQLModel


class RoleBase(SQLModel):
    role_name: str = Field(
        max_length=50,
        description="Nom du rôle (ADMIN, PROF, etc.)",
        nullable=False,
    )


class RoleCreateDTO(RoleBase):
    pass


class RoleUpdateDTO(SQLModel):
    role_name: str | None = None


class RoleResponseDTO(RoleBase):
    id: int

