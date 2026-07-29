"""modulo tarefas

Revision ID: df72887d6333
Revises: 303001c0b0e6
Create Date: 2026-07-22 18:56:57.097732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df72887d6333'
down_revision: Union[str, None] = '303001c0b0e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Recria o enum modulo_sistema incluindo 'TAREFAS' (Postgres não tem ALTER TYPE ... ADD VALUE
    # de forma simples/segura de reverter, então trocamos a coluna para texto, recriamos o tipo e convertemos de volta).
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE VARCHAR(20)")
    op.execute("DROP TYPE modulo_sistema")
    op.execute("CREATE TYPE modulo_sistema AS ENUM ('CLIENTES', 'PROCESSOS', 'PRAZOS', 'FINANCEIRO', 'TAREFAS')")
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE modulo_sistema USING modulo::modulo_sistema")

    status_tarefa = sa.Enum('PENDENTE', 'CONCLUIDA', name='status_tarefa')

    op.create_table(
        'tarefas',
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('data_vencimento', sa.Date(), nullable=True),
        sa.Column('status', status_tarefa, nullable=False),
        sa.Column('processo_id', sa.Uuid(), nullable=True),
        sa.Column('responsavel_id', sa.Uuid(), nullable=True),
        sa.Column('criado_por_id', sa.Uuid(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['processo_id'], ['processos.id']),
        sa.ForeignKeyConstraint(['responsavel_id'], ['users.id']),
        sa.ForeignKeyConstraint(['criado_por_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # funcionários já existentes recebem acesso total ao novo módulo, seguindo o padrão
    # do sistema (todo módulo nasce liberado; o super_admin restringe depois se quiser)
    op.execute(
        """
        INSERT INTO permissoes (id, user_id, modulo, pode_visualizar, pode_editar, pode_excluir, created_at, updated_at)
        SELECT gen_random_uuid(), id, 'TAREFAS', true, true, true, now(), now()
        FROM users WHERE super_admin = false
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissoes WHERE modulo = 'TAREFAS'")
    op.drop_table('tarefas')
    op.execute("DROP TYPE status_tarefa")

    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE VARCHAR(20)")
    op.execute("DROP TYPE modulo_sistema")
    op.execute("CREATE TYPE modulo_sistema AS ENUM ('CLIENTES', 'PROCESSOS', 'PRAZOS', 'FINANCEIRO')")
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE modulo_sistema USING modulo::modulo_sistema")
