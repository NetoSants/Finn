-- Finn Database Schema

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

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transacoes_user_id ON transacoes(user_id);
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo);
CREATE INDEX IF NOT EXISTS idx_parcelas_user_id ON parcelas(user_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_pago ON parcelas(pago);