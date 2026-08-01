import logging
from bot.database import get_conn, put_conn

logger = logging.getLogger(__name__)

MIGRATIONS = [
    # Tabela categorias
    """
    CREATE TABLE IF NOT EXISTS categorias (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(50) NOT NULL UNIQUE,
        emoji VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # Categorias padrao
    """
    INSERT INTO categorias (nome, emoji) VALUES
        ('Alimentação', '🍔'),
        ('Transporte', '🚗'),
        ('Moradia', '🏠'),
        ('Saúde', '💊'),
        ('Lazer', '🎮'),
        ('Educação', '📚'),
        ('Roupa', '👕'),
        ('Serviços', '🔧'),
        ('Outros', '📦')
    ON CONFLICT (nome) DO NOTHING;
    """,
    # Coluna categoria_id na tabela transacoes
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'transacoes' AND column_name = 'categoria_id'
        ) THEN
            ALTER TABLE transacoes ADD COLUMN categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL;
        END IF;
    END $$;
    """,
    # Tabela metas
    """
    CREATE TABLE IF NOT EXISTS metas (
        id SERIAL PRIMARY KEY,
        categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
        mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
        ano INTEGER NOT NULL,
        limite DECIMAL(12,2) NOT NULL,
        user_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(categoria_id, mes, ano, user_id)
    );
    """,
    # Indices
    """
    CREATE INDEX IF NOT EXISTS idx_transacoes_categoria ON transacoes(categoria_id);
    CREATE INDEX IF NOT EXISTS idx_metas_user_mes ON metas(user_id, mes, ano);
    """,
    # Tabela fixos (gastos/rendas recorrentes)
    """
    CREATE TABLE IF NOT EXISTS fixos (
        id SERIAL PRIMARY KEY,
        tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('gasto', 'renda')),
        valor DECIMAL(12,2) NOT NULL,
        descricao VARCHAR(255) NOT NULL,
        categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
        pagamento VARCHAR(20) DEFAULT 'debito',
        banco_id INTEGER REFERENCES bancos(id) ON DELETE SET NULL,
        parcelas INTEGER DEFAULT 1,
        dia INTEGER NOT NULL CHECK (dia >= 1 AND dia <= 31),
        ativo BOOLEAN DEFAULT TRUE,
        user_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # Indices fixos
    """
    CREATE INDEX IF NOT EXISTS idx_fixos_user_id ON fixos(user_id);
    """,
    # Coluna fixo_origin_id nas transacoes (para rastrear geracao automatica)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'transacoes' AND column_name = 'fixo_origin_id'
        ) THEN
            ALTER TABLE transacoes ADD COLUMN fixo_origin_id INTEGER REFERENCES fixos(id) ON DELETE SET NULL;
        END IF;
    END $$;
    """,
    # Coluna fatura_paga nas transacoes (controle de pagamento de faturas)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'transacoes' AND column_name = 'fatura_paga'
        ) THEN
            ALTER TABLE transacoes ADD COLUMN fatura_paga BOOLEAN DEFAULT FALSE;
        END IF;
    END $$;
    """,
]


def run_migrations():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            for i, sql in enumerate(MIGRATIONS):
                cur.execute(sql)
                logger.debug(f"Migration {i+1}/{len(MIGRATIONS)} OK")
        conn.commit()
        logger.info("Migrations concluidas")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro nas migrations: {e}")
        raise
    finally:
        put_conn(conn)
