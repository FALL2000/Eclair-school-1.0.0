from typing import Optional

from sqlmodel import Field, SQLModel

from common.enumeration import TypeEtablissement


class EtablissementBase(SQLModel):
    libelle: str = Field(
        unique=True, max_length=150, nullable=False, description="Nom unique de l'etablissement")
    region: str = Field(
        max_length=60, nullable=False, description="Region de l'etablissement")
    ville: str = Field(
        max_length=60, nullable=False, description="Ville de l'etablissement")
    quartier: str = Field(
        max_length=100, nullable=False, description="Quartier de l'etablissement")
    type: TypeEtablissement = Field(
        nullable=False, description="Type d'etablissement : Primaire ou Secondaire")
    # Lien vers l'image du logo, renseigne apres l'upload du fichier. None = pas encore de logo
    logo: Optional[str] = Field(
        default=None, max_length=255, nullable=True, description="Lien vers l'image du logo (upload)")


class EtablissementCreateDTO(EtablissementBase):
    pass


class EtablissementUpdateDTO(SQLModel):
    libelle: Optional[str] = None
    region: Optional[str] = None
    ville: Optional[str] = None
    quartier: Optional[str] = None
    type: Optional[TypeEtablissement] = None
    logo: Optional[str] = None


class EtablissementResponseDTO(EtablissementBase):
    id: int
