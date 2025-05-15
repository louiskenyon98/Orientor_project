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
    # Add career_id column to saved_recommendations table
    op.add_column('saved_recommendations', sa.Column('career_id', sa.Integer(), nullable=True))
    
    # Create an index on career_id for better query performance
    op.create_index(op.f('ix_saved_recommendations_career_id'), 'saved_recommendations', ['career_id'], unique=False)

def downgrade():
    # Remove the index and column
    op.drop_index(op.f('ix_saved_recommendations_career_id'), table_name='saved_recommendations')
    op.drop_column('saved_recommendations', 'career_id') 