"""add private analysis history"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_analysis_history"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analysis_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("primary_emotion", sa.String(48), nullable=False, index=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("distribution_json", sa.Text(), nullable=False),
        sa.Column("valence", sa.Float(), nullable=False),
        sa.Column("arousal", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("sample_rate", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(180), nullable=False),
        sa.Column("source_type", sa.String(24), nullable=False, server_default="upload", index=True),
        sa.Column("source_name", sa.String(180), nullable=False, server_default="Voice sample"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("analysis_records")
