from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(length=128), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True)
    )
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_table('locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('venue_name', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('state', sa.String(length=64), nullable=True),
        sa.Column('country', sa.String(length=64), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_table('sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False, unique=True),
        sa.Column('base_url', sa.String(length=512), nullable=True),
        sa.Column('robots_ok', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('crawl_delay_ms', sa.Integer(), nullable=True),
        sa.Column('last_robots_fetch', sa.DateTime(), nullable=True)
    )
    op.create_table('programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('organizer', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('source_url', sa.String(length=1024), nullable=False),
        sa.Column('snapshot_url', sa.String(length=1024), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='new'),
        sa.Column('category', sa.String(length=128), nullable=True),
        sa.Column('subcategory', sa.String(length=128), nullable=True),
        sa.Column('start_datetime', sa.DateTime(), nullable=True),
        sa.Column('end_datetime', sa.DateTime(), nullable=True),
        sa.Column('timezone', sa.String(length=64), nullable=True),
        sa.Column('recurrence', sa.String(length=64), nullable=True),
        sa.Column('venue_name', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('state', sa.String(length=64), nullable=True),
        sa.Column('country', sa.String(length=64), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('online_flag', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('audience_age_min', sa.Integer(), nullable=True),
        sa.Column('audience_age_max', sa.Integer(), nullable=True),
        sa.Column('price_amount', sa.Float(), nullable=True),
        sa.Column('price_currency', sa.String(length=8), nullable=True),
        sa.Column('free_flag', sa.Boolean(), nullable=True),
        sa.Column('description_text', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=True),
        sa.Column('provenance', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('reason_tags', sa.JSON(), nullable=True),
        sa.Column('dedupe_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_programs_category_start_city', 'programs', ['category','start_datetime','city'])
    op.create_index('ix_programs_dedupe_hash', 'programs', ['dedupe_hash'])

    op.create_table('snapshots',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id')),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    op.create_table('runs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='running'),
        sa.Column('inserted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_samples', sa.JSON(), nullable=True)
    )

    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('actor', sa.String(length=128), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('target_id', sa.String(length=64), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('audit_log')
    op.drop_table('runs')
    op.drop_table('snapshots')
    op.drop_index('ix_programs_dedupe_hash', table_name='programs')
    op.drop_index('ix_programs_category_start_city', table_name='programs')
    op.drop_table('programs')
    op.drop_table('sources')
    op.drop_table('locations')
    op.drop_table('organizations')
