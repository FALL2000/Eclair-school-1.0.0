"""initial_data

Revision ID: 5c7db25559e3
Revises: 585eb30305ca
Create Date: 2026-03-28 11:06:19.142542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from config.settings import get_settings


# revision identifiers, used by Alembic.
revision: str = '5c7db25559e3'
down_revision: Union[str, Sequence[str], None] = '585eb30305ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = get_settings()


def upgrade() -> None:
    """Upgrade schema."""
    cycle_data = []
    section_data = [
        {'id': 1, 'code': "ANGLO", 'libelle': "ANGLOPHONE"},
        {'id': 2, 'code': "FRANCO", 'libelle': "FRANCOPHONE"},
        {'id': 3, 'code': "BIL", 'libelle': "BILINGUE"},
    ]
    trimestre_data = [
        {'id': 1, 'code': "TRIM-1", 'libelle': "TRIMESTRE 1"},
        {'id': 2, 'code': "TRIM-2", 'libelle': "TRIMESTRE 2"},
        {'id': 3, 'code': "TRIM-3", 'libelle': "TRIMESTRE 3"},
    ]

    serie_data = [
        {'id': 1, 'code': "ALL", 'libelle': "ALLEMAND"},
        {'id': 2, 'code': "ESP", 'libelle': "ESPAGNOL"},
        {'id': 3, 'code': "CHN", 'libelle': "CHINOIS"},
        {'id': 4, 'code': "A4 ALL", 'libelle': "A4 ALL"},
        {'id': 5, 'code': "A4 ESP", 'libelle': "A4 ESP"},
        {'id': 6, 'code': "A4 CHN", 'libelle': "A4 CHN"},
        {'id': 7, 'code': "C", 'libelle': "C"},
        {'id': 8, 'code': "D", 'libelle': "D"},
        {'id': 9, 'code': "E", 'libelle': "E"},
        {'id': 10, 'code': "F1", 'libelle': "F1"},
        {'id': 11, 'code': "F2", 'libelle': "F2"},
        {'id': 12, 'code': "F3", 'libelle': "F3"},
        {'id': 13, 'code': "F4", 'libelle': "F4"},
        {'id': 14, 'code': "IH", 'libelle': "IH"},
        {'id': 15, 'code': "G", 'libelle': "G"},
        {'id': 16, 'code': "TI", 'libelle': "TI"},
    ]
    if settings.type_school == "education_base":
        cycle_data = [
            {'id': 1, 'code': "MAT-FRANCO", 'libelle': "MATERNELLE", 'id_section': 2},
            {'id': 2, 'code': "NUR-ANGLO", 'libelle': "NURSERY", 'id_section': 1},
            {'id': 3, 'code': "PRI-FRANCO", 'libelle': "PRIMAIRE", 'id_section': 2},
            {'id': 4, 'code': "PRI-ANGLO", 'libelle': "PRIMARY", 'id_section': 1},
            {'id': 5, 'code': "PRI-BIL", 'libelle': "PRIMAIRE BIL", 'id_section': 3},
            {'id': 6, 'code': "MAT-BIL", 'libelle': "MATERNELLE BIL", 'id_section': 3},
        ]
    elif settings.type_school == "secondaire":
        cycle_data = [
            {'id': 1, 'code': "FRANCO-1", 'libelle': "PREMIER CYCLE", 'id_section': 2},
            {'id': 2, 'code': "ANGLO-1", 'libelle': "FIRST CYCLE", 'id_section': 1},
            {'id': 3, 'code': "FRANCO-2", 'libelle': "SECOND CYCLE", 'id_section': 2},
            {'id': 4, 'code': "ANGLO-2", 'libelle': "SECOND CYCLE", 'id_section': 1},
            {'id': 5, 'code': "BIL-1", 'libelle': "PREMIER CYCLE BIL", 'id_section': 3},
            {'id': 6, 'code': "BIL-2", 'libelle': "SECOND CYCLE BIL", 'id_section': 3},
        ]
    section_table = sa.table('section',
                             sa.column('id', sa.Integer),
                             sa.column('code', sa.String),
                             sa.column('libelle', sa.String)
                             )
    serie_table = sa.table('serie',
                           sa.column('id', sa.Integer),
                           sa.column('code', sa.String),
                           sa.column('libelle', sa.String)
                           )
    trimestre_table = sa.table('trimestre',
                               sa.column('id', sa.Integer),
                               sa.column('code', sa.String),
                               sa.column('libelle', sa.String)
                               )
    cycle_table = sa.table('cycle',
                           sa.column('id', sa.Integer),
                           sa.column('code', sa.String),
                           sa.column('libelle', sa.String),
                           sa.column('id_section', sa.String)
                           )

    op.bulk_insert(section_table, section_data)
    if settings.type_school == "secondaire":
        op.bulk_insert(serie_table, serie_data)
    op.bulk_insert(trimestre_table, trimestre_data)
    op.bulk_insert(cycle_table, cycle_data)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM cycle")
    op.execute("DELETE FROM section")
    if settings.type_school == "secondaire":
        op.execute("DELETE FROM serie")
    op.execute("DELETE FROM trimestre")
