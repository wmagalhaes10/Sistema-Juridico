"""modulo publicacoes djen

Revision ID: e3970a514744
Revises: df72887d6333
Create Date: 2026-07-24 20:38:54.928307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3970a514744'
down_revision: Union[str, None] = 'df72887d6333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # inclui 'PUBLICACOES' no enum modulo_sistema (mesma técnica da migration de tarefas)
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE VARCHAR(20)")
    op.execute("DROP TYPE modulo_sistema")
    op.execute(
        "CREATE TYPE modulo_sistema AS ENUM "
        "('CLIENTES', 'PROCESSOS', 'PRAZOS', 'FINANCEIRO', 'TAREFAS', 'PUBLICACOES')"
    )
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE modulo_sistema USING modulo::modulo_sistema")

    status_publicacao = sa.Enum('NAO_TRATADA', 'TRATADA', 'DESCARTADA', name='status_publicacao')

    op.create_table(
        'publicacoes',
        sa.Column('id_djen', sa.BigInteger(), nullable=False),
        sa.Column('data_disponibilizacao', sa.Date(), nullable=False),
        sa.Column('sigla_tribunal', sa.String(length=20), nullable=True),
        sa.Column('tipo_comunicacao', sa.String(length=100), nullable=True),
        sa.Column('tipo_documento', sa.String(length=100), nullable=True),
        sa.Column('nome_orgao', sa.String(length=255), nullable=True),
        sa.Column('nome_classe', sa.String(length=255), nullable=True),
        sa.Column('numero_processo', sa.String(length=25), nullable=True),
        sa.Column('texto', sa.Text(), nullable=True),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('meio', sa.String(length=100), nullable=True),
        sa.Column('oab_numero', sa.String(length=20), nullable=True),
        sa.Column('oab_uf', sa.String(length=2), nullable=True),
        sa.Column('status', status_publicacao, nullable=False),
        sa.Column('processo_id', sa.Uuid(), nullable=True),
        sa.Column('tratada_por_id', sa.Uuid(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['processo_id'], ['processos.id']),
        sa.ForeignKeyConstraint(['tratada_por_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_publicacoes_id_djen', 'publicacoes', ['id_djen'], unique=True)
    op.create_index('ix_publicacoes_data_disponibilizacao', 'publicacoes', ['data_disponibilizacao'])
    op.create_index('ix_publicacoes_numero_processo', 'publicacoes', ['numero_processo'])

    # funcionários existentes recebem acesso total ao novo módulo (padrão do sistema)
    op.execute(
        """
        INSERT INTO permissoes (id, user_id, modulo, pode_visualizar, pode_editar, pode_excluir, created_at, updated_at)
        SELECT gen_random_uuid(), id, 'PUBLICACOES', true, true, true, now(), now()
        FROM users WHERE super_admin = false
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissoes WHERE modulo = 'PUBLICACOES'")
    op.drop_index('ix_publicacoes_numero_processo', table_name='publicacoes')
    op.drop_index('ix_publicacoes_data_disponibilizacao', table_name='publicacoes')
    op.drop_index('ix_publicacoes_id_djen', table_name='publicacoes')
    op.drop_table('publicacoes')
    op.execute("DROP TYPE status_publicacao")

    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE VARCHAR(20)")
    op.execute("DROP TYPE modulo_sistema")
    op.execute(
        "CREATE TYPE modulo_sistema AS ENUM ('CLIENTES', 'PROCESSOS', 'PRAZOS', 'FINANCEIRO', 'TAREFAS')"
    )
    op.execute("ALTER TABLE permissoes ALTER COLUMN modulo TYPE modulo_sistema USING modulo::modulo_sistema")
