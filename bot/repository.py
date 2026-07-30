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

def inserir_transacao(tipo, valor, descricao, pagamento, user_id, username, categoria_id=None, banco_id=None, parcelas=1):
    return _insert(
        "INSERT INTO transacoes (tipo, valor, descricao, pagamento, user_id, username, categoria_id, banco_id, parcelas) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (tipo, valor, descricao, pagamento, user_id, username, categoria_id, banco_id, parcelas)
    )


def inserir_renda(valor, descricao, user_id, username):
    return _insert(
        "INSERT INTO transacoes (tipo, valor, descricao, user_id, username) VALUES ('renda', %s, %s, %s, %s)",
        (valor, descricao, user_id, username)
    )


def listar_transacoes(user_id, limite=20):
    return _fetch(
        """SELECT t.tipo, t.valor, t.descricao, t.pagamento, t.data_transacao, c.nome, c.emoji
           FROM transacoes t
           LEFT JOIN categorias c ON c.id = t.categoria_id
           WHERE t.user_id = %s ORDER BY t.created_at DESC LIMIT %s""",
        (user_id, limite)
    )


def listar_transacoes_periodo(user_id, mes, ano, limite=50):
    return _fetch(
        """SELECT t.tipo, t.valor, t.descricao, t.pagamento, t.data_transacao, c.nome, c.emoji
           FROM transacoes t
           LEFT JOIN categorias c ON c.id = t.categoria_id
           WHERE t.user_id = %s
               AND EXTRACT(MONTH FROM t.data_transacao) = %s
               AND EXTRACT(YEAR FROM t.data_transacao) = %s
           ORDER BY t.created_at DESC LIMIT %s""",
        (user_id, mes, ano, limite)
    )


def listar_transacoes_csv(user_id):
    return _fetch(
        """SELECT t.tipo, t.valor, t.descricao, t.pagamento, t.data_transacao,
                  c.nome, c.emoji, t.created_at
           FROM transacoes t
           LEFT JOIN categorias c ON c.id = t.categoria_id
           WHERE t.user_id = %s
           ORDER BY t.created_at DESC""",
        (user_id,)
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


def gastos_hoje(user_id):
    return _fetch_one(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'gasto' AND user_id = %s AND data_transacao = CURRENT_DATE",
        (user_id,)
    )[0]


def buscar_categoria_por_id(cat_id):
    return _fetch_one(
        "SELECT id, nome, emoji FROM categorias WHERE id = %s",
        (cat_id,)
    )


# --- Categorias ---

def listar_categorias():
    return _fetch("SELECT id, nome, emoji FROM categorias ORDER BY id")


def buscar_categoria_por_nome(nome):
    return _fetch_one(
        "SELECT id, nome, emoji FROM categorias WHERE LOWER(nome) = LOWER(%s)",
        (nome,)
    )


def criar_categoria(nome, emoji=None):
    return _insert(
        "INSERT INTO categorias (nome, emoji) VALUES (%s, %s)",
        (nome, emoji)
    )


# --- Metas ---

def definir_meta(categoria_id, mes, ano, limite, user_id):
    return _execute(
        """INSERT INTO metas (categoria_id, mes, ano, limite, user_id)
           VALUES (%s, %s, %s, %s, %s)
           ON CONFLICT (categoria_id, mes, ano, user_id)
           DO UPDATE SET limite = EXCLUDED.limite""",
        (categoria_id, mes, ano, limite, user_id)
    )


def buscar_meta(categoria_id, mes, ano, user_id):
    return _fetch_one(
        "SELECT id, limite FROM metas WHERE categoria_id = %s AND mes = %s AND ano = %s AND user_id = %s",
        (categoria_id, mes, ano, user_id)
    )


def listar_metas(mes, ano, user_id):
    return _fetch(
        """SELECT m.id, c.nome, c.emoji, m.limite,
                  COALESCE(SUM(t.valor), 0) as gasto_total
           FROM metas m
           JOIN categorias c ON c.id = m.categoria_id
           LEFT JOIN transacoes t ON t.categoria_id = m.categoria_id
               AND t.tipo = 'gasto' AND t.user_id = m.user_id
               AND EXTRACT(MONTH FROM t.data_transacao) = m.mes
               AND EXTRACT(YEAR FROM t.data_transacao) = m.ano
           WHERE m.mes = %s AND m.ano = %s AND m.user_id = %s
           GROUP BY m.id, c.nome, c.emoji, m.limite
           ORDER BY c.nome""",
        (mes, ano, user_id)
    )


def gasto_por_categoria(user_id, mes, ano):
    return _fetch(
        """SELECT c.nome, c.emoji, COALESCE(SUM(t.valor), 0) as total
           FROM categorias c
           LEFT JOIN transacoes t ON t.categoria_id = c.id
               AND t.tipo = 'gasto' AND t.user_id = %s
               AND EXTRACT(MONTH FROM t.data_transacao) = %s
               AND EXTRACT(YEAR FROM t.data_transacao) = %s
           GROUP BY c.id, c.nome, c.emoji
           HAVING COALESCE(SUM(t.valor), 0) > 0
           ORDER BY total DESC""",
        (user_id, mes, ano)
    )


def total_gastos_periodo(user_id, mes, ano):
    return _fetch_one(
        """SELECT COALESCE(SUM(valor), 0) FROM transacoes
           WHERE tipo = 'gasto' AND user_id = %s
               AND EXTRACT(MONTH FROM data_transacao) = %s
               AND EXTRACT(YEAR FROM data_transacao) = %s""",
        (user_id, mes, ano)
    )[0]


def total_rendas_periodo(user_id, mes, ano):
    return _fetch_one(
        """SELECT COALESCE(SUM(valor), 0) FROM transacoes
           WHERE tipo = 'renda' AND user_id = %s
               AND EXTRACT(MONTH FROM data_transacao) = %s
               AND EXTRACT(YEAR FROM data_transacao) = %s""",
        (user_id, mes, ano)
    )[0]


def maior_gasto(user_id, mes, ano):
    return _fetch_one(
        """SELECT valor, descricao, data_transacao FROM transacoes
           WHERE tipo = 'gasto' AND user_id = %s
               AND EXTRACT(MONTH FROM data_transacao) = %s
               AND EXTRACT(YEAR FROM data_transacao) = %s
           ORDER BY valor DESC LIMIT 1""",
        (user_id, mes, ano)
    )


def dias_com_gastos(user_id, mes, ano):
    return _fetch_one(
        """SELECT COUNT(DISTINCT data_transacao) FROM transacoes
           WHERE tipo = 'gasto' AND user_id = %s
               AND EXTRACT(MONTH FROM data_transacao) = %s
               AND EXTRACT(YEAR FROM data_transacao) = %s""",
        (user_id, mes, ano)
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


# --- Fixos ---

def inserir_fixo(tipo, valor, descricao, pagamento, user_id, categoria_id=None, banco_id=None, parcelas=1, dia=1):
    return _insert(
        "INSERT INTO fixos (tipo, valor, descricao, pagamento, user_id, categoria_id, banco_id, parcelas, dia) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (tipo, valor, descricao, pagamento, user_id, categoria_id, banco_id, parcelas, dia)
    )


def remover_fixo(fixo_id, user_id):
    return _execute("DELETE FROM fixos WHERE id = %s AND user_id = %s", (fixo_id, user_id))


def listar_fixos(user_id):
    return _fetch(
        """SELECT f.id, f.tipo, f.valor, f.descricao, f.pagamento, f.parcelas, f.dia, f.ativo,
                  c.nome, c.emoji, b.nome
           FROM fixos f
           LEFT JOIN categorias c ON c.id = f.categoria_id
           LEFT JOIN bancos b ON b.id = f.banco_id
           WHERE f.user_id = %s
           ORDER BY f.tipo, f.dia""",
        (user_id,)
    )


def buscar_fixo(fixo_id, user_id):
    return _fetch_one(
        "SELECT id, tipo, valor, descricao, pagamento, categoria_id, banco_id, parcelas, dia, ativo FROM fixos WHERE id = %s AND user_id = %s",
        (fixo_id, user_id)
    )


def toggle_fixo(fixo_id, user_id):
    return _execute(
        "UPDATE fixos SET ativo = NOT ativo WHERE id = %s AND user_id = %s",
        (fixo_id, user_id)
    )
