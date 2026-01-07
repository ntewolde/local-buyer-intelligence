"""Initial schema with multi-tenancy and new models

Revision ID: 2024_01_01_0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_01_01_0001'
down_revision = '2024_01_01_0000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'analyst', 'client', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_client_id'), 'users', ['client_id'], unique=False)
    
    # Update geographies table - add client_id and freshness fields
    op.add_column('geographies', sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('geographies', sa.Column('census_last_refreshed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('geographies', sa.Column('property_last_refreshed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('geographies', sa.Column('events_last_refreshed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('geographies', sa.Column('channels_last_refreshed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_geographies_client_id'), 'geographies', ['client_id'], unique=False)
    op.create_foreign_key('fk_geographies_client_id', 'geographies', 'clients', ['client_id'], ['id'])
    # Note: For existing data, you may need to set a default client_id or handle migration separately
    
    # Update households table - add client_id and census_block_group
    op.add_column('households', sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('households', sa.Column('census_block_group', sa.String(length=12), nullable=True))
    op.create_index(op.f('ix_households_client_id'), 'households', ['client_id'], unique=False)
    op.create_index(op.f('ix_households_census_block_group'), 'households', ['census_block_group'], unique=False)
    op.create_foreign_key('fk_households_client_id', 'households', 'clients', ['client_id'], ['id'])
    
    # Update demand_signals table - add client_id, value, and metadata
    op.add_column('demand_signals', sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('demand_signals', sa.Column('value', sa.Float(), nullable=True))
    op.add_column('demand_signals', sa.Column('signal_metadata', sa.Text(), nullable=True))
    op.alter_column('demand_signals', 'geography_id', nullable=True)
    op.alter_column('demand_signals', 'zip_code_id', nullable=True)
    # Add DEMOGRAPHIC to SignalType enum (if not using check constraint, update enum)
    op.create_index(op.f('ix_demand_signals_client_id'), 'demand_signals', ['client_id'], unique=False)
    op.create_foreign_key('fk_demand_signals_client_id', 'demand_signals', 'clients', ['client_id'], ['id'])
    
    # Update intelligence_reports table - add client_id column
    op.add_column('intelligence_reports', sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_intelligence_reports_client_id'), 'intelligence_reports', ['client_id'], unique=False)
    op.create_foreign_key('fk_intelligence_reports_client_id', 'intelligence_reports', 'clients', ['client_id'], ['id'])
    
    # Create channels table
    op.create_table(
        'channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('channel_type', sa.Enum('HOA', 'PROPERTY_MANAGER', 'SCHOOL', 'CHURCH', 'VENUE', 'MEDIA', 'COMMUNITY_NEWSLETTER', 'OTHER', name='channeltype'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=255), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('estimated_reach', sa.Integer(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channels_id'), 'channels', ['id'], unique=False)
    op.create_index(op.f('ix_channels_client_id'), 'channels', ['client_id'], unique=False)
    op.create_index(op.f('ix_channels_geography_id'), 'channels', ['geography_id'], unique=False)
    op.create_index(op.f('ix_channels_zip_code'), 'channels', ['zip_code'], unique=False)
    
    # Create ingestion_runs table
    op.create_table(
        'ingestion_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('source_type', sa.Enum('census', 'csv_property', 'csv_events', 'csv_channels', name='sourcetype'), nullable=False),
        sa.Column('status', sa.Enum('queued', 'running', 'success', 'failed', name='ingestionstatus'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_upserted', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('file_ref', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingestion_runs_id'), 'ingestion_runs', ['id'], unique=False)
    op.create_index(op.f('ix_ingestion_runs_client_id'), 'ingestion_runs', ['client_id'], unique=False)
    op.create_index(op.f('ix_ingestion_runs_geography_id'), 'ingestion_runs', ['geography_id'], unique=False)


def downgrade() -> None:
    # Drop ingestion_runs table
    op.drop_index(op.f('ix_ingestion_runs_geography_id'), table_name='ingestion_runs')
    op.drop_index(op.f('ix_ingestion_runs_client_id'), table_name='ingestion_runs')
    op.drop_index(op.f('ix_ingestion_runs_id'), table_name='ingestion_runs')
    op.drop_table('ingestion_runs')
    
    # Drop channels table
    op.drop_index(op.f('ix_channels_zip_code'), table_name='channels')
    op.drop_index(op.f('ix_channels_geography_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_client_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_id'), table_name='channels')
    op.drop_table('channels')
    
    # Revert intelligence_reports
    op.drop_constraint('fk_intelligence_reports_client_id', 'intelligence_reports', type_='foreignkey')
    op.drop_index(op.f('ix_intelligence_reports_client_id'), table_name='intelligence_reports')
    op.drop_column('intelligence_reports', 'client_id')
    
    # Revert demand_signals
    op.drop_constraint('fk_demand_signals_client_id', 'demand_signals', type_='foreignkey')
    op.drop_index(op.f('ix_demand_signals_client_id'), table_name='demand_signals')
    op.drop_column('demand_signals', 'signal_metadata')
    op.drop_column('demand_signals', 'value')
    op.drop_column('demand_signals', 'client_id')
    op.alter_column('demand_signals', 'geography_id', nullable=False)
    op.alter_column('demand_signals', 'zip_code_id', nullable=False)
    
    # Revert households
    op.drop_constraint('fk_households_client_id', 'households', type_='foreignkey')
    op.drop_index(op.f('ix_households_census_block_group'), table_name='households')
    op.drop_index(op.f('ix_households_client_id'), table_name='households')
    op.drop_column('households', 'census_block_group')
    op.drop_column('households', 'client_id')
    
    # Revert geographies
    op.drop_constraint('fk_geographies_client_id', 'geographies', type_='foreignkey')
    op.drop_index(op.f('ix_geographies_client_id'), table_name='geographies')
    op.drop_column('geographies', 'channels_last_refreshed_at')
    op.drop_column('geographies', 'events_last_refreshed_at')
    op.drop_column('geographies', 'property_last_refreshed_at')
    op.drop_column('geographies', 'census_last_refreshed_at')
    op.drop_column('geographies', 'client_id')
    
    # Drop users table
    op.drop_index(op.f('ix_users_client_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop clients table
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_table('clients')
    
    # Drop enums (if needed)
    op.execute('DROP TYPE IF EXISTS channeltype')
    op.execute('DROP TYPE IF EXISTS sourcetype')
    op.execute('DROP TYPE IF EXISTS ingestionstatus')
    op.execute('DROP TYPE IF EXISTS userrole')

