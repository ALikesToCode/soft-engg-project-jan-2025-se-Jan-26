"""Add lecture transcription model

Revision ID: 20250816_first
Create Date: 2025-08-16 14:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250816_first'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lecture_transcriptions table
    op.create_table(
        'lecture_transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lecture_id', sa.Integer(), nullable=False),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['lecture_id'], ['lectures.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for faster lookups
    op.create_index(op.f('ix_lecture_transcriptions_lecture_id'), 'lecture_transcriptions', ['lecture_id'], unique=True)


def downgrade() -> None:
    # Drop the table and indexes
    op.drop_index(op.f('ix_lecture_transcriptions_lecture_id'), table_name='lecture_transcriptions')
    op.drop_table('lecture_transcriptions') 