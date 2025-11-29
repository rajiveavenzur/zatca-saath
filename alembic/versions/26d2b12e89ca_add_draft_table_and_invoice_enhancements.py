"""Mako template for generating migrations."""

"""add_draft_table_and_invoice_enhancements

Revision ID: 26d2b12e89ca
Revises: 30a433690956
Create Date: 2025-11-29 18:55:12.338490

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '26d2b12e89ca'
down_revision = '30a433690956'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create invoice_drafts table
    op.create_table(
        'invoice_drafts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('draft_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('is_auto_saved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_drafts_user_id'), 'invoice_drafts', ['user_id'], unique=False)
    
    # Add status column to invoices table
    op.add_column('invoices', sa.Column('status', sa.String(length=20), nullable=True, server_default='generated'))
    
    # Add indexes to invoices table for better performance
    op.create_index('idx_invoice_user_date', 'invoices', ['user_id', 'invoice_date'], unique=False)
    op.create_index('idx_invoice_customer', 'invoices', ['customer_name_ar'], unique=False)
    op.create_index(op.f('ix_invoices_created_at'), 'invoices', ['created_at'], unique=False)


def downgrade() -> None:
    # Remove indexes from invoices
    op.drop_index(op.f('ix_invoices_created_at'), table_name='invoices')
    op.drop_index('idx_invoice_customer', table_name='invoices')
    op.drop_index('idx_invoice_user_date', table_name='invoices')
    
    # Remove status column from invoices
    op.drop_column('invoices', 'status')
    
    # Drop invoice_drafts table
    op.drop_index(op.f('ix_invoice_drafts_user_id'), table_name='invoice_drafts')
    op.drop_table('invoice_drafts')
