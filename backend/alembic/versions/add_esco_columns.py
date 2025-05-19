"""Add ESCO columns to user_profiles

Revision ID: add_esco_columns
Revises: add_oasis_columns
Create Date: 2025-05-19 12:37:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_esco_columns'
down_revision = 'add_oasis_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les colonnes pour stocker les profils formatés selon le style ESCO
    op.add_column('user_profiles', sa.Column('esco_occupation_profile', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('esco_skill_profile', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('esco_skillsgroup_profile', sa.Text(), nullable=True))
    op.add_column('user_profiles', sa.Column('esco_full_profile', sa.Text(), nullable=True))
    
    # Ajouter la colonne pour stocker l'embedding généré à partir du profil ESCO complet
    op.add_column('user_profiles', sa.Column('esco_embedding', JSONB(), nullable=True))
    
    # Ajouter un index sur la colonne esco_embedding pour améliorer les performances de recherche
    op.create_index(op.f('ix_user_profiles_esco_embedding'), 'user_profiles', ['esco_embedding'], unique=False)


def downgrade():
    # Supprimer l'index
    op.drop_index(op.f('ix_user_profiles_esco_embedding'), table_name='user_profiles')
    
    # Supprimer les colonnes
    op.drop_column('user_profiles', 'esco_embedding')
    op.drop_column('user_profiles', 'esco_full_profile')
    op.drop_column('user_profiles', 'esco_skillsgroup_profile')
    op.drop_column('user_profiles', 'esco_skill_profile')
    op.drop_column('user_profiles', 'esco_occupation_profile')