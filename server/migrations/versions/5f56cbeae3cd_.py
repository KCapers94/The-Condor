"""empty message

Revision ID: 5f56cbeae3cd
Revises: 6c1c36f3025d
Create Date: 2025-01-14 13:24:26.748071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f56cbeae3cd'
down_revision = '6c1c36f3025d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dates', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.INTEGER(),
               type_=sa.Date(),
               existing_nullable=True)
        batch_op.alter_column('time',
               existing_type=sa.INTEGER(),
               type_=sa.Time(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dates', schema=None) as batch_op:
        batch_op.alter_column('time',
               existing_type=sa.Time(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.Date(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
