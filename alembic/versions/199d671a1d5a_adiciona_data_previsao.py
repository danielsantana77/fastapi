"""Adiciona data previsao

Revision ID: 199d671a1d5a
Revises: ca506c08d989
Create Date: 2024-05-07 15:22:53.028431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '199d671a1d5a'
down_revision: Union[str, None] = 'ca506c08d989'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contas_a_pagar_e_receber', sa.Column('data_previsao', sa.DateTime(), nullable=True))
    op.execute("update contas_a_pagar_e_receber set data_previsao = now()")
    op.alter_column("contas_a_pagar_e_receber", 'data_previsao', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contas_a_pagar_e_receber', 'data_previsao')
    # ### end Alembic commands ###
