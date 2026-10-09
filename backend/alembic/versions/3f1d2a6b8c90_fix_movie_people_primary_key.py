"""Use the association ID as the movie_people primary key.

Revision ID: 3f1d2a6b8c90
Revises: 5b038c11ce44
Create Date: 2026-10-09
"""
from typing import Sequence, Union

from alembic import op


revision: str = "3f1d2a6b8c90"
down_revision: Union[str, Sequence[str], None] = "5b038c11ce44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE movie_people_id_seq")
    op.execute(
        "SELECT setval('movie_people_id_seq', "
        "COALESCE((SELECT MAX(id) FROM movie_people), 0) + 1, false)"
    )
    op.execute(
        "ALTER TABLE movie_people "
        "ALTER COLUMN id SET DEFAULT nextval('movie_people_id_seq')"
    )
    op.execute("ALTER SEQUENCE movie_people_id_seq OWNED BY movie_people.id")

    op.drop_constraint("movie_people_pkey", "movie_people", type_="primary")
    op.create_primary_key("pk_movie_people", "movie_people", ["id"])


def downgrade() -> None:
    op.drop_constraint("pk_movie_people", "movie_people", type_="primary")
    op.execute("ALTER TABLE movie_people ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE movie_people_id_seq")
    op.create_primary_key(
        "movie_people_pkey", "movie_people", ["id", "movie_id", "person_id"]
    )
