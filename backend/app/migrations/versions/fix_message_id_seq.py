"""Fix message_id_seq

Revision ID: fix_message_id_seq
Revises: update_saved_recommendations
Create Date: 2024-04-26 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_message_id_seq'
down_revision = 'update_saved_recommendations'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the sequence if it exists
    op.execute("DROP SEQUENCE IF EXISTS message_id_seq")
    
    # Create the sequence with proper ownership
    op.execute("""
        CREATE SEQUENCE message_id_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    """)
    
    # Set the sequence as owned by the messages table
    op.execute("ALTER SEQUENCE message_id_seq OWNED BY messages.message_id")
    
    # Set the default value for message_id column
    op.execute("ALTER TABLE messages ALTER COLUMN message_id SET DEFAULT nextval('message_id_seq')")

def downgrade():
    # Remove the default value
    op.execute("ALTER TABLE messages ALTER COLUMN message_id DROP DEFAULT")
    
    # Drop the sequence
    op.execute("DROP SEQUENCE IF EXISTS message_id_seq") 