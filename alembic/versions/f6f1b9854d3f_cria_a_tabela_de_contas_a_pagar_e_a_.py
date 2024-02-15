"""Cria a tabela de contas a pagar e a receber

Revision ID: f6f1b9854d3f
Revises: 
Create Date: 2024-01-12 21:15:56.776045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6f1b9854d3f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contas_a_pagar_e_receber',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('descricao', sa.String(length=30), nullable=True),
    sa.Column('valor', sa.Numeric(), nullable=True),
    sa.Column('tipo', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contas_a_pagar_e_receber')
    # ### end Alembic commands ###