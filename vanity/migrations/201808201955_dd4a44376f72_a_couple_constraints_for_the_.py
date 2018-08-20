"""a couple constraints for the association table

Revision ID: dd4a44376f72
Revises: 2c2a1826f5d0
Create Date: 2018-08-20 19:55:53.601511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd4a44376f72'
down_revision = '96daae59325b'
branch_labels = ()
depends_on = None


def upgrade():
    with op.batch_alter_table('vanity_association', schema=None) as batch_op:
        batch_op.create_primary_key('pk_vanity_association', ['post_id', 'user_id'])
        batch_op.alter_column('post_id', nullable=False)
        batch_op.alter_column('user_id', nullable=False)


def downgrade():
    with op.batch_alter_table('vanity_association', schema=None) as batch_op:
        batch_op.drop_constraint('pk_vanity_association', type_='primary')
        batch_op.alter_column('post_id', nullable=True)
        batch_op.alter_column('user_id', nullable=True)
