"""Add future work models (Option 2, 3, 4, 5)

Revision ID: 2024_01_02_0000
Revises: 2024_01_01_0001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_01_02_0000'
down_revision = '2024_01_01_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add channel CRM fields (Option 4)
    op.add_column('channels', sa.Column('quality_score', sa.Integer(), nullable=True))
    op.add_column('channels', sa.Column('engagement_score', sa.Integer(), nullable=True))
    op.add_column('channels', sa.Column('last_contacted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('channels', sa.Column('contact_status', sa.String(length=50), nullable=True))
    op.add_column('channels', sa.Column('outreach_notes', sa.Text(), nullable=True))
    
    # Create channel_outreaches table (Option 4)
    op.create_table(
        'channel_outreaches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('outreach_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.Enum('planned', 'contacted', 'responded', 'followed_up', 'partnered', 'declined', 'no_response', name='outreachstatus'), nullable=False),
        sa.Column('method', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('response_received', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_followup_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channel_outreaches_id'), 'channel_outreaches', ['id'], unique=False)
    op.create_index(op.f('ix_channel_outreaches_client_id'), 'channel_outreaches', ['client_id'], unique=False)
    op.create_index(op.f('ix_channel_outreaches_channel_id'), 'channel_outreaches', ['channel_id'], unique=False)
    
    # Create campaigns table (Option 5)
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('service_category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('draft', 'planned', 'active', 'paused', 'completed', 'cancelled', name='campaignstatus'), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_budget', sa.Float(), nullable=True),
        sa.Column('budget_allocation', sa.JSON(), nullable=True),
        sa.Column('channel_ids', sa.JSON(), nullable=True),
        sa.Column('assets', sa.JSON(), nullable=True),
        sa.Column('messaging', sa.Text(), nullable=True),
        sa.Column('target_reach', sa.Integer(), nullable=True),
        sa.Column('actual_reach', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('target_leads', sa.Integer(), nullable=True),
        sa.Column('actual_leads', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_client_id'), 'campaigns', ['client_id'], unique=False)
    
    # Create campaign_reports table (Option 5)
    op.create_table(
        'campaign_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('channel_performance', sa.JSON(), nullable=True),
        sa.Column('insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_reports_id'), 'campaign_reports', ['id'], unique=False)
    op.create_index(op.f('ix_campaign_reports_client_id'), 'campaign_reports', ['client_id'], unique=False)
    op.create_index(op.f('ix_campaign_reports_campaign_id'), 'campaign_reports', ['campaign_id'], unique=False)
    
    # Create landing_pages table (Option 2)
    op.create_table(
        'landing_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('service_category', sa.String(length=50), nullable=False),
        sa.Column('city_name', sa.String(length=255), nullable=True),
        sa.Column('state_code', sa.String(length=2), nullable=True),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('call_to_action', sa.String(length=255), nullable=True),
        sa.Column('consent_types', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_landing_pages_id'), 'landing_pages', ['id'], unique=False)
    op.create_index(op.f('ix_landing_pages_slug'), 'landing_pages', ['slug'], unique=True)
    op.create_index(op.f('ix_landing_pages_client_id'), 'landing_pages', ['client_id'], unique=False)
    
    # Create leads table (Option 2)
    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('landing_page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('geography_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('email_consent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sms_consent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consent_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('consent_ip', sa.String(length=45), nullable=True),
        sa.Column('status', sa.Enum('new', 'contacted', 'qualified', 'converted', 'unsubscribed', name='leadstatus'), nullable=False),
        sa.Column('service_category', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('assigned_to_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('last_contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['landing_page_id'], ['landing_pages.id'], ),
        sa.ForeignKeyConstraint(['geography_id'], ['geographies.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=False)
    op.create_index(op.f('ix_leads_client_id'), 'leads', ['client_id'], unique=False)
    op.create_index(op.f('ix_leads_landing_page_id'), 'leads', ['landing_page_id'], unique=False)
    op.create_index(op.f('ix_leads_zip_code'), 'leads', ['zip_code'], unique=False)


def downgrade() -> None:
    # Drop leads table
    op.drop_index(op.f('ix_leads_zip_code'), table_name='leads')
    op.drop_index(op.f('ix_leads_landing_page_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_client_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_index(op.f('ix_leads_id'), table_name='leads')
    op.drop_table('leads')
    
    # Drop landing_pages table
    op.drop_index(op.f('ix_landing_pages_client_id'), table_name='landing_pages')
    op.drop_index(op.f('ix_landing_pages_slug'), table_name='landing_pages')
    op.drop_index(op.f('ix_landing_pages_id'), table_name='landing_pages')
    op.drop_table('landing_pages')
    
    # Drop campaign_reports table
    op.drop_index(op.f('ix_campaign_reports_campaign_id'), table_name='campaign_reports')
    op.drop_index(op.f('ix_campaign_reports_client_id'), table_name='campaign_reports')
    op.drop_index(op.f('ix_campaign_reports_id'), table_name='campaign_reports')
    op.drop_table('campaign_reports')
    
    # Drop campaigns table
    op.drop_index(op.f('ix_campaigns_client_id'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')
    
    # Drop channel_outreaches table
    op.drop_index(op.f('ix_channel_outreaches_channel_id'), table_name='channel_outreaches')
    op.drop_index(op.f('ix_channel_outreaches_client_id'), table_name='channel_outreaches')
    op.drop_index(op.f('ix_channel_outreaches_id'), table_name='channel_outreaches')
    op.drop_table('channel_outreaches')
    
    # Remove channel CRM fields
    op.drop_column('channels', 'outreach_notes')
    op.drop_column('channels', 'contact_status')
    op.drop_column('channels', 'last_contacted_at')
    op.drop_column('channels', 'engagement_score')
    op.drop_column('channels', 'quality_score')

