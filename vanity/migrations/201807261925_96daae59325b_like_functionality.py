"""like functionality

Revision ID: 96daae59325b
Create Date: 2018-07-26 19:25:41.164377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96daae59325b'
down_revision = None
branch_labels = ()
depends_on = None


def upgrade():
    op.create_table('vanity_association',
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name=op.f('fk_vanity_association_post_id_posts')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_vanity_association_user_id_users'))
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('likes_received', sa.Integer()))
        batch_op.add_column(sa.Column('likes_given', sa.Integer()))

    op.execute('''
        UPDATE users
           SET likes_received = 0,
               likes_given    = 0
    ''')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('likes_received', nullable=False)
        batch_op.alter_column('likes_given', nullable=False)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('likes_received')
        batch_op.drop_column('likes_given')

    op.drop_table('vanity_association')
