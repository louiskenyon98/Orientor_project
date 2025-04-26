"""add message_id_seq

Revision ID: add_message_id_seq
Revises: 
Create Date: 2024-04-26 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_message_id_seq'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the sequence
    op.execute("CREATE SEQUENCE IF NOT EXISTS message_id_seq START WITH 1 INCREMENT BY 1")

def downgrade():
    # Drop the sequence
    op.execute("DROP SEQUENCE IF EXISTS message_id_seq") 