"""Update saved_recommendations table

Revision ID: update_saved_recommendations
Revises: add_message_id_seq
Create Date: 2024-04-26 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_saved_recommendations'
down_revision = 'add_message_id_seq'
branch_labels = None
depends_on = None

def upgrade():
    # We don't need to add career_id as it doesn't match the existing schema
    pass

def downgrade():
    # Nothing to downgrade
    pass 