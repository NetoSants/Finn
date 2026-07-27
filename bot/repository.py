from bot.database import get_conn, put_conn


def _fetch(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        put_conn(conn)


def _fetch_one(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.fetchone()
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)


def _execute(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)


def _insert(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query + " RETURNING id", params)
            conn.commit()
            return cur.fetchone()[0]
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)


# --- Transacoes ---

def inserir_transacao(tipo, valor, descricao, pagamento, user_id, username):
    return _insert(
        "INSERT INTO transacoes (tipo, valor, descricao, pagamento, user_id, username) VALUES (%s, %s, %s, %s, %s, %s)",
        (tipo, valor, descricao, pagamento, user_id, username)
    )


def inserir_renda(valor, descricao, user_id, username):
    return _insert(
        "INSERT INTO transacoes (tipo, valor, descricao, user_id, username) VALUES ('renda', %s, %s, %s, %s)",
        (valor, descricao, user_id, username)
    )


def listar_transacoes(user_id, limite=20):
    return _fetch(
        "SELECT tipo, valor, descricao, pagamento, data_transacao FROM transacoes WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limite)
    )


def total_gastos(user_id):
    return _fetch_one(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'gasto' AND user_id = %s",
        (user_id,)
    )[0]


def total_rendas(user_id):
    return _fetch_one(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'renda' AND user_id = %s",
        (user_id,)
    )[0]


def contar_transacoes(user_id):
    return _fetch_one(
        "SELECT COUNT(*) FROM transacoes WHERE user_id = %s",
        (user_id,)
    )[0]


# --- Bancos ---

def inserir_banco(nome, dia_fechamento, limite):
    return _insert(
        "INSERT INTO bancos (nome, dia_fechamento, limite) VALUES (%s, %s, %s)",
        (nome, dia_fechamento, limite)
    )


def remover_banco(nome):
    return _execute("DELETE FROM bancos WHERE nome = %s", (nome,))


def listar_bancos():
    return _fetch("SELECT id, nome, dia_fechamento, limite FROM bancos ORDER BY nome")


def contar_bancos():
    return _fetch_one("SELECT COUNT(*) FROM bancos")[0]


# --- Parcelas ---

def inserir_parcela(descricao, valor_total, valor_parcela, numero_parcelas, data_primeira_parcela, user_id, username):
    return _insert(
        "INSERT INTO parcelas (descricao, valor_total, valor_parcela, numero_parcelas, data_primeira_parcela, user_id, username) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (descricao, valor_total, valor_parcela, numero_parcelas, data_primeira_parcela, user_id, username)
    )


def listar_parcelas(user_id):
    return _fetch(
        "SELECT id, descricao, valor_total, valor_parcela, numero_parcelas, numero_parcela_atual, pago, data_primeira_parcela FROM parcelas WHERE user_id = %s ORDER BY data_primeira_parcela",
        (user_id,)
    )
