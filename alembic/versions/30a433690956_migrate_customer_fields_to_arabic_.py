"""Mako template for generating migrations."""

"""migrate_customer_fields_to_arabic_mandatory

Revision ID: 30a433690956
Revises: 
Create Date: 2025-11-29 02:25:32.136162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30a433690956'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns for Arabic and English customer information
    op.add_column('invoices', sa.Column('customer_name_ar', sa.String(length=200), nullable=True))
    op.add_column('invoices', sa.Column('customer_name_en', sa.String(length=200), nullable=True))
    op.add_column('invoices', sa.Column('customer_address_ar', sa.String(length=500), nullable=True))
    op.add_column('invoices', sa.Column('customer_address_en', sa.String(length=500), nullable=True))
    
    # Migrate existing data - copy to Arabic fields (assuming existing data is Arabic)
    op.execute("""
        UPDATE invoices 
        SET customer_name_ar = customer_name,
            customer_address_ar = customer_address
    """)
    
    # Make Arabic fields non-nullable (they are now populated)
    op.alter_column('invoices', 'customer_name_ar', nullable=False)
    op.alter_column('invoices', 'customer_address_ar', nullable=False)
    
    # Drop old columns
    op.drop_column('invoices', 'customer_name')
    op.drop_column('invoices', 'customer_address')


def downgrade() -> None:
    # Add back old columns
    op.add_column('invoices', sa.Column('customer_name', sa.String(length=200), nullable=True))
    op.add_column('invoices', sa.Column('customer_address', sa.String(length=500), nullable=True))
    
    # Copy data from Arabic fields to old fields
    op.execute("""
        UPDATE invoices 
        SET customer_name = customer_name_ar,
            customer_address = customer_address_ar
    """)
    
    # Make old columns non-nullable
    op.alter_column('invoices', 'customer_name', nullable=False)
    op.alter_column('invoices', 'customer_address', nullable=False)
    
    # Drop new columns
    op.drop_column('invoices', 'customer_address_en')
    op.drop_column('invoices', 'customer_address_ar')
    op.drop_column('invoices', 'customer_name_en')
    op.drop_column('invoices', 'customer_name_ar')
