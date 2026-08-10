"""store profile image in backend"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_backend_profile_storage"
down_revision: Union[str, None] = "0002_analysis_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("avatar_data", sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column("avatar_mime", sa.String(length=48), nullable=True))
        batch_op.add_column(sa.Column("avatar_updated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("avatar_updated_at")
        batch_op.drop_column("avatar_mime")
        batch_op.drop_column("avatar_data")
