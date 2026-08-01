-- Finn Database Schema

-- Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    emoji VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

-- Bancos (cartões de crédito)
CREATE TABLE IF NOT EXISTS bancos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    dia_fechamento INTEGER NOT NULL CHECK (dia_fechamento >= 1 AND dia_fechamento <= 31),
    limite DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transações (gastos e rendas)
CREATE TABLE IF NOT EXISTS transacoes (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('gasto', 'renda')),
    valor DECIMAL(12,2) NOT NULL,
    descricao TEXT,
    pagamento VARCHAR(20) CHECK (pagamento IN ('debito', 'credito', 'pix', NULL)),
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    banco_id INTEGER REFERENCES bancos(id) ON DELETE SET NULL,
    data_transacao DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id BIGINT NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parcelas
CREATE TABLE IF NOT EXISTS parcelas (
    id SERIAL PRIMARY KEY,
    descricao TEXT NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL,
    valor_parcela DECIMAL(12,2) NOT NULL,
    numero_parcelas INTEGER NOT NULL,
    numero_parcela_atual INTEGER NOT NULL DEFAULT 1,
    banco_id INTEGER REFERENCES bancos(id) ON DELETE SET NULL,
    pago BOOLEAN DEFAULT FALSE,
    data_primeira_parcela DATE NOT NULL,
    user_id BIGINT NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metas mensais por categoria
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

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transacoes_user_id ON transacoes(user_id);
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo);
CREATE INDEX IF NOT EXISTS idx_transacoes_categoria ON transacoes(categoria_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_user_id ON parcelas(user_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_pago ON parcelas(pago);
CREATE INDEX IF NOT EXISTS idx_metas_user_mes ON metas(user_id, mes, ano);

-- Fixos (gastos/rendas recorrentes)
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
CREATE INDEX IF NOT EXISTS idx_fixos_user_id ON fixos(user_id);

-- Referencia para geracao automatica de lancamentos a partir de fixos
ALTER TABLE transacoes ADD COLUMN IF NOT EXISTS fixo_origin_id INTEGER REFERENCES fixos(id) ON DELETE SET NULL;

-- Controle de pagamento de faturas (credito)
ALTER TABLE transacoes ADD COLUMN IF NOT EXISTS fatura_paga BOOLEAN DEFAULT FALSE;