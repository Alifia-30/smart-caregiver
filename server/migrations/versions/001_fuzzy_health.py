"""add_fuzzy_fields_to_health_records

Revision ID: 001_fuzzy_health
Revises: 
Create Date: 2026-04-28

Changes:
  health_records table:
    - ADD cholesterol         FLOAT (metabolic module)
    - ADD uric_acid           FLOAT (metabolic module)
    - ADD spo2_level          FLOAT (cardiovascular + infection modules)
    - ADD cardio_score        FLOAT (fuzzy output)
    - ADD metabolic_score     FLOAT (fuzzy output)
    - ADD infection_score     FLOAT (fuzzy output)
    - ADD fuzzy_final_score   FLOAT (averaged fuzzy output)

  health_status column type:
    - ADD new allowed value 'warning' to the String(20) column
      (PostgreSQL String column — no ALTER TYPE needed; value is stored as-is)

NOTE: Run with:
    cd server
    alembic revision --autogenerate -m "add_fuzzy_fields_to_health_records"
    alembic upgrade head

OR apply this migration manually:
    alembic upgrade 001_fuzzy_health
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_fuzzy_health"
down_revision = None   # update this to the last existing revision id if applicable
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── New measurement columns ────────────────────────────────────────────────
    op.add_column(
        "health_records",
        sa.Column("cholesterol", sa.Float(), nullable=True, comment="mg/dL — metabolic module"),
    )
    op.add_column(
        "health_records",
        sa.Column("uric_acid", sa.Float(), nullable=True, comment="mg/dL — metabolic module"),
    )
    op.add_column(
        "health_records",
        sa.Column("spo2_level", sa.Float(), nullable=True, comment="% — cardiovascular & infection modules"),
    )

    # ── Fuzzy score columns ────────────────────────────────────────────────────
    op.add_column(
        "health_records",
        sa.Column("cardio_score", sa.Float(), nullable=True, comment="Fuzzy cardiovascular score 0-100"),
    )
    op.add_column(
        "health_records",
        sa.Column("metabolic_score", sa.Float(), nullable=True, comment="Fuzzy metabolic score 0-100"),
    )
    op.add_column(
        "health_records",
        sa.Column("infection_score", sa.Float(), nullable=True, comment="Fuzzy infection score 0-100"),
    )
    op.add_column(
        "health_records",
        sa.Column("fuzzy_final_score", sa.Float(), nullable=True, comment="Fuzzy final averaged score 0-100"),
    )


def downgrade() -> None:
    op.drop_column("health_records", "fuzzy_final_score")
    op.drop_column("health_records", "infection_score")
    op.drop_column("health_records", "metabolic_score")
    op.drop_column("health_records", "cardio_score")
    op.drop_column("health_records", "spo2_level")
    op.drop_column("health_records", "uric_acid")
    op.drop_column("health_records", "cholesterol")
