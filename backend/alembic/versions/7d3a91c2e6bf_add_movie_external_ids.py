"""add external provider identifiers for movies

Revision ID: 7d3a91c2e6bf
Revises: c1fc5abc3682
Create Date: 2026-10-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d3a91c2e6bf"
down_revision: Union[str, Sequence[str], None] = "c1fc5abc3682"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movie_external_ids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.CheckConstraint(
            "provider IN ('tmdb', 'imdb')",
            name="ck_movie_external_ids_provider",
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "external_id", name="uq_movie_external_ids_provider_id"
        ),
        sa.UniqueConstraint(
            "movie_id", "provider", name="uq_movie_external_ids_movie_provider"
        ),
    )
    op.create_index(
        op.f("ix_movie_external_ids_movie_id"),
        "movie_external_ids",
        ["movie_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_movie_external_ids_movie_id"), table_name="movie_external_ids")
    op.drop_table("movie_external_ids")