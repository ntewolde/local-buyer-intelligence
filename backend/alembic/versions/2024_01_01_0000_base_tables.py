"""Create base tables (if not exists from manual setup)

Revision ID: 2024_01_01_0000
Revises: 
Create Date: 2024-01-01 00:00:00.000000

This migration creates base tables. If tables already exist from manual setup,
you may need to handle data migration separately.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_01_01_0000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create geographies table (if not exists)
    op.create_table(
        'geographies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('state_code', sa.String(length=2), nullable=False),
        sa.Column('county_name', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_geographies_id'), 'geographies', ['id'], unique=False)
    op.create_index(op.f('ix_geographies_name'), 'geographies', ['name'], unique=False)
    op.create_index(op.f('ix_geographies_state_code'), 'geographies', ['state_code'], unique=False)
    
    # Create zip_codes table
    op.create_table(
        'zip_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('zip_code', sa.String(length=10), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('household_count', sa.Integer(), nullable=True),
        sa.Column('median_income', sa.Integer(), nullable=True),
        sa.Column('median_age', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zip_code')
    )
    op.create_index(op.f('ix_zip_codes_id'), 'zip_codes', ['id'], unique=False)
    op.create_index(op.f('ix_zip_codes_zip_code'), 'zip_codes', ['zip_code'], unique=True)
    
    # Create neighborhoods table
    op.create_table(
        'neighborhoods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('zip_code_id', sa.Integer(), nullable=True),
        sa.Column('boundary_geojson', sa.String(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('household_count', sa.Integer(), nullable=True),
        sa.Column('median_income', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.ForeignKeyConstraint(['zip_code_id'], ['zip_codes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_neighborhoods_id'), 'neighborhoods', ['id'], unique=False)
    op.create_index(op.f('ix_neighborhoods_name'), 'neighborhoods', ['name'], unique=False)
    
    # Create households table
    op.create_table(
        'households',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('zip_code_id', sa.Integer(), nullable=True),
        sa.Column('neighborhood_id', sa.Integer(), nullable=True),
        sa.Column('property_type', sa.Enum('single_family', 'multi_family', 'condo', 'apartment', 'mobile_home', 'commercial', 'unknown', name='propertytype'), nullable=True),
        sa.Column('ownership_type', sa.Enum('owner', 'renter', 'unknown', name='ownershiptype'), nullable=True),
        sa.Column('property_sqft_min', sa.Integer(), nullable=True),
        sa.Column('property_sqft_max', sa.Integer(), nullable=True),
        sa.Column('lot_size_sqft', sa.Integer(), nullable=True),
        sa.Column('income_band_min', sa.Integer(), nullable=True),
        sa.Column('income_band_max', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('property_age_years', sa.Integer(), nullable=True),
        sa.Column('last_sale_year', sa.Integer(), nullable=True),
        sa.Column('lawn_care_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('security_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('it_services_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('fireworks_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('general_service_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_source', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.ForeignKeyConstraint(['zip_code_id'], ['zip_codes.id'], ),
        sa.ForeignKeyConstraint(['neighborhood_id'], ['neighborhoods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_households_id'), 'households', ['id'], unique=False)
    
    # Create demand_signals table
    op.create_table(
        'demand_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('zip_code_id', sa.Integer(), nullable=True),
        sa.Column('signal_type', sa.Enum('event', 'permit', 'seasonal', 'turnover', 'weather', 'census', 'demographic', 'custom', name='signaltype'), nullable=False),
        sa.Column('service_category', sa.Enum('lawn_care', 'security', 'it_services', 'fireworks', 'home_improvement', 'cleaning', 'pest_control', 'hvac', 'plumbing', 'electrical', 'general', name='servicecategory'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('relevance_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('relevance_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('demand_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('source_name', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('source_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.ForeignKeyConstraint(['zip_code_id'], ['zip_codes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demand_signals_id'), 'demand_signals', ['id'], unique=False)
    
    # Create intelligence_reports table
    op.create_table(
        'intelligence_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('zip_codes', sa.String(), nullable=True),
        sa.Column('service_category', sa.String(length=50), nullable=True),
        sa.Column('report_name', sa.String(length=255), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_households', sa.Integer(), nullable=True),
        sa.Column('target_households', sa.Integer(), nullable=True),
        sa.Column('average_demand_score', sa.Float(), nullable=True),
        sa.Column('buyer_profile', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('zip_demand_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('neighborhood_insights', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('channel_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timing_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('report_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intelligence_reports_id'), 'intelligence_reports', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_intelligence_reports_id'), table_name='intelligence_reports')
    op.drop_table('intelligence_reports')
    op.drop_index(op.f('ix_demand_signals_id'), table_name='demand_signals')
    op.drop_table('demand_signals')
    op.drop_index(op.f('ix_households_id'), table_name='households')
    op.drop_table('households')
    op.drop_index(op.f('ix_neighborhoods_name'), table_name='neighborhoods')
    op.drop_index(op.f('ix_neighborhoods_id'), table_name='neighborhoods')
    op.drop_table('neighborhoods')
    op.drop_index(op.f('ix_zip_codes_zip_code'), table_name='zip_codes')
    op.drop_index(op.f('ix_zip_codes_id'), table_name='zip_codes')
    op.drop_table('zip_codes')
    op.drop_index(op.f('ix_geographies_state_code'), table_name='geographies')
    op.drop_index(op.f('ix_geographies_name'), table_name='geographies')
    op.drop_index(op.f('ix_geographies_id'), table_name='geographies')
    op.drop_table('geographies')






