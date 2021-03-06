"""empty message

Revision ID: b22fef35255b
Revises: 549d7813b4b9
Create Date: 2020-04-19 11:06:01.424005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b22fef35255b'
down_revision = '549d7813b4b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('fellower_id', sa.Integer(), nullable=False),
    sa.Column('fellowed_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['fellowed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['fellower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('fellower_id', 'fellowed_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follows')
    # ### end Alembic commands ###
