"""Add recoverable parent accounts and revocable sessions without touching lessons."""
from alembic import op
import sqlalchemy as sa

revision = '0003_accounts'
down_revision = '0002_voice_teaching'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('family_id', sa.String(36), nullable=False, unique=True),
        sa.Column('username', sa.String(32), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(250), nullable=False),
        sa.Column('credential_version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False))
    op.create_table('auth_sessions',
        sa.Column('token_hash', sa.String(64), primary_key=True),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('account_id', sa.String(36), nullable=True),
        sa.Column('credential_version', sa.Integer(), nullable=False),
        sa.Column('csrf', sa.String(64), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False),
        sa.Column('last_seen_at', sa.Float(), nullable=False),
        sa.Column('expires_at', sa.Float(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False),
        sa.Column('parent_hash', sa.String(64), nullable=False),
        sa.Column('parent_expires', sa.Float(), nullable=False))
    op.create_index('ix_auth_sessions_family_id', 'auth_sessions', ['family_id'])
    op.create_index('ix_auth_sessions_account_id', 'auth_sessions', ['account_id'])
    op.create_table('auth_rate_limits',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.Float(), nullable=False))
    op.create_index('ix_auth_rate_limits_expires_at', 'auth_rate_limits', ['expires_at'])


def downgrade():
    op.drop_table('auth_rate_limits')
    op.drop_table('auth_sessions')
    op.drop_table('accounts')
