"""Parent voice opt-in and durable narration assistance evidence."""
from alembic import op
import sqlalchemy as sa

revision = '0002_voice_teaching'
down_revision = '0001_family_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Server defaults safely backfill existing families and learning records.
    op.add_column('families', sa.Column('voice_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('learning_records', sa.Column('narrations', sa.JSON(), nullable=False, server_default='{}'))


def downgrade():
    op.drop_column('learning_records', 'narrations')
    op.drop_column('families', 'voice_enabled')
