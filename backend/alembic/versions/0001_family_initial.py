"""Initial isolated Tarka Family schema."""
from alembic import op
import sqlalchemy as sa

revision = '0001_family_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'families',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('csrf', sa.String(64), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False),
        sa.Column('pin_hash', sa.String(200), nullable=False),
        sa.Column('nickname', sa.String(20), nullable=False),
        sa.Column('age_band', sa.String(10), nullable=False),
        sa.Column('ai_enabled', sa.Boolean(), nullable=False),
        sa.Column('session_minutes', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.Float(), nullable=False),
        sa.Column('break_until', sa.Float(), nullable=False),
        sa.Column('parent_hash', sa.String(64), nullable=False),
        sa.Column('parent_expires', sa.Float(), nullable=False),
    )
    op.create_table(
        'lessons',
        sa.Column('id', sa.String(30), primary_key=True),
        sa.Column('data', sa.JSON(), nullable=False),
    )
    op.create_table(
        'learning_records',
        sa.Column('id', sa.String(80), primary_key=True),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('lesson_id', sa.String(30), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('hints', sa.JSON(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('transfer_independent', sa.Boolean(), nullable=False),
    )
    op.create_index('ix_learning_records_family_id', 'learning_records', ['family_id'])
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('provider', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('model', sa.String(150), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('reserved_usd', sa.Float(), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False),
    )
    op.create_index('ix_usage_logs_family_id', 'usage_logs', ['family_id'])
    op.create_table(
        'budget',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reserved_usd', sa.Float(), nullable=False),
    )


def downgrade():
    # Explicit operator action only: this removes all v2 application tables/data.
    op.drop_table('budget')
    op.drop_index('ix_usage_logs_family_id', table_name='usage_logs')
    op.drop_table('usage_logs')
    op.drop_index('ix_learning_records_family_id', table_name='learning_records')
    op.drop_table('learning_records')
    op.drop_table('lessons')
    op.drop_table('families')
