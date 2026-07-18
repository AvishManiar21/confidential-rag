"""Initial migration - create documents and query_audit tables

Revision ID: 001
Revises:
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('num_chunks', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('embedding_hash', sa.String(length=64), nullable=True),
        sa.Column('commitment', sa.String(length=64), nullable=True),
        sa.Column('merkle_root', sa.String(length=64), nullable=True),
        sa.Column('merkle_proof', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('tx_hash', sa.String(length=66), nullable=True),
        sa.Column('block_number', sa.Integer(), nullable=True),
        sa.Column('contract_address', sa.String(length=42), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for documents
    op.create_index('ix_documents_filename', 'documents', ['filename'])
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'], unique=True)
    op.create_index('ix_documents_embedding_hash', 'documents', ['embedding_hash'])
    op.create_index('ix_documents_commitment', 'documents', ['commitment'])
    op.create_index('ix_documents_merkle_root', 'documents', ['merkle_root'])
    op.create_index('ix_documents_processed', 'documents', ['processed'])
    op.create_index('ix_documents_tx_hash', 'documents', ['tx_hash'])

    # Create query_audit table
    op.create_table(
        'query_audit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('query_hash', sa.String(length=64), nullable=False),
        sa.Column('num_results', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('retrieved_docs', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('relevance_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('response_hash', sa.String(length=64), nullable=True),
        sa.Column('proof_generated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('proof_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('proof_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('ragas_score', sa.Float(), nullable=True),
        sa.Column('avg_similarity', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for query_audit
    op.create_index('ix_query_audit_query_hash', 'query_audit', ['query_hash'])
    op.create_index('ix_query_audit_proof_generated', 'query_audit', ['proof_generated'])
    op.create_index('ix_query_audit_proof_verified', 'query_audit', ['proof_verified'])
    op.create_index('ix_query_audit_user_id', 'query_audit', ['user_id'])
    op.create_index('ix_query_audit_session_id', 'query_audit', ['session_id'])
    op.create_index('ix_query_audit_status', 'query_audit', ['status'])
    op.create_index('ix_query_audit_created_at', 'query_audit', ['created_at'])


def downgrade() -> None:
    # Drop query_audit table and indexes
    op.drop_index('ix_query_audit_created_at', table_name='query_audit')
    op.drop_index('ix_query_audit_status', table_name='query_audit')
    op.drop_index('ix_query_audit_session_id', table_name='query_audit')
    op.drop_index('ix_query_audit_user_id', table_name='query_audit')
    op.drop_index('ix_query_audit_proof_verified', table_name='query_audit')
    op.drop_index('ix_query_audit_proof_generated', table_name='query_audit')
    op.drop_index('ix_query_audit_query_hash', table_name='query_audit')
    op.drop_table('query_audit')

    # Drop documents table and indexes
    op.drop_index('ix_documents_tx_hash', table_name='documents')
    op.drop_index('ix_documents_processed', table_name='documents')
    op.drop_index('ix_documents_merkle_root', table_name='documents')
    op.drop_index('ix_documents_commitment', table_name='documents')
    op.drop_index('ix_documents_embedding_hash', table_name='documents')
    op.drop_index('ix_documents_file_hash', table_name='documents')
    op.drop_index('ix_documents_filename', table_name='documents')
    op.drop_table('documents')
