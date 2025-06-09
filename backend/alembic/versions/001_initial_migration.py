"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import pgvector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('job_title', sa.String(100), nullable=True),
        sa.Column('role', sa.Enum('admin', 'user', 'viewer', name='userrole'), nullable=False, default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('sso_provider', sa.String(50), nullable=True),
        sa.Column('sso_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create meetings table
    op.create_table('meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('participants', postgresql.JSON(), nullable=False, default=[]),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('scheduled', 'in_progress', 'completed', 'cancelled', name='meetingstatus'), nullable=False, default='scheduled'),
        sa.Column('processing_status', sa.Enum('pending', 'transcribing', 'embedding', 'analyzing', 'completed', 'failed', name='processingstatus'), nullable=False, default='pending'),
        sa.Column('s3_audio_uri', sa.String(500), nullable=True),
        sa.Column('s3_transcript_uri', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False, default={}),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_cost_usd', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create segments table
    op.create_table('segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id'), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('start_time_seconds', sa.Float(), nullable=False),
        sa.Column('end_time_seconds', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(100), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column('transcription_confidence', sa.Float(), nullable=True),
        sa.Column('speaker_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create template_runs table
    op.create_table('template_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id'), nullable=False),
        sa.Column('template_type', sa.Enum('key_points', 'action_items', 'decisions', 'risks', 'blockers', 'follow_ups', 'parking_lot', 'roadmap', 'kudos', name='templatetype'), nullable=False),
        sa.Column('template_version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('user_prompt', sa.Text(), nullable=False),
        sa.Column('raw_response', sa.Text(), nullable=False),
        sa.Column('structured_output', postgresql.JSON(), nullable=False, default={}),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('model_name', sa.String(50), nullable=False),
        sa.Column('model_parameters', postgresql.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create insights table
    op.create_table('insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id'), nullable=False),
        sa.Column('template_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('template_runs.id'), nullable=True),
        sa.Column('insight_type', sa.Enum('key_points', 'action_items', 'decisions', 'risks', 'blockers', 'follow_ups', 'parking_lot', 'roadmap', 'kudos', name='templatetype'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSON(), nullable=False, default={}),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes for better performance
    
    # Meetings indexes
    op.create_index('ix_meetings_status', 'meetings', ['status'])
    op.create_index('ix_meetings_processing_status', 'meetings', ['processing_status'])
    op.create_index('ix_meetings_created_at', 'meetings', ['created_at'])
    op.create_index('ix_meetings_organizer_id', 'meetings', ['organizer_id'])
    op.create_index('ix_meetings_is_deleted', 'meetings', ['is_deleted'])
    
    # Segments indexes
    op.create_index('ix_segments_meeting_id', 'segments', ['meeting_id'])
    op.create_index('ix_segments_sequence_number', 'segments', ['sequence_number'])
    op.create_index('ix_segments_start_time', 'segments', ['start_time_seconds'])
    
    # Vector index for semantic search
    op.execute('CREATE INDEX IF NOT EXISTS ix_segments_embedding_ivfflat ON segments USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    
    # Insights indexes
    op.create_index('ix_insights_meeting_id', 'insights', ['meeting_id'])
    op.create_index('ix_insights_insight_type', 'insights', ['insight_type'])
    op.create_index('ix_insights_created_at', 'insights', ['created_at'])
    
    # Template runs indexes
    op.create_index('ix_template_runs_meeting_id', 'template_runs', ['meeting_id'])
    op.create_index('ix_template_runs_template_type', 'template_runs', ['template_type'])
    op.create_index('ix_template_runs_created_at', 'template_runs', ['created_at'])
    
    # Users indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('insights')
    op.drop_table('template_runs')
    op.drop_table('segments')
    op.drop_table('meetings')
    op.drop_table('users')
    
    # Drop custom enums
    op.execute('DROP TYPE IF EXISTS templatetype')
    op.execute('DROP TYPE IF EXISTS processingstatus')
    op.execute('DROP TYPE IF EXISTS meetingstatus')
    op.execute('DROP TYPE IF EXISTS userrole')