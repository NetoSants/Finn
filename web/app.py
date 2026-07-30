import os
from decimal import Decimal
from datetime import date
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bot.database import get_conn, put_conn

app = FastAPI(title="Finn", docs_url=None, redoc_url=None)

USER_ID = int(os.getenv("ALLOWED_USER_IDS", "1401845586").split(",")[0].strip())

templates = Jinja2Templates(directory="web/templates")


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
            return cur.fetchone()
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


def _fmt(valor):
    if valor is None:
        return "0,00"
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


templates.env.filters["fmt"] = _fmt


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, mes: int = Query(default=None), ano: int = Query(default=None)):
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    total_gastos = _fetch_one(
        "SELECT COALESCE(SUM(valor),0) FROM transacoes WHERE tipo='gasto' AND user_id=%s AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s",
        (USER_ID, mes, ano)
    )[0]

    total_rendas = _fetch_one(
        "SELECT COALESCE(SUM(valor),0) FROM transacoes WHERE tipo='renda' AND user_id=%s AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s",
        (USER_ID, mes, ano)
    )[0]

    saldo = total_rendas - total_gastos

    gastos_hoje = _fetch_one(
        "SELECT COALESCE(SUM(valor),0) FROM transacoes WHERE tipo='gasto' AND user_id=%s AND data_transacao=CURRENT_DATE",
        (USER_ID,)
    )[0]

    maior_gasto = _fetch_one(
        "SELECT valor, descricao FROM transacoes WHERE tipo='gasto' AND user_id=%s AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s ORDER BY valor DESC LIMIT 1",
        (USER_ID, mes, ano)
    )

    total_transacoes = _fetch_one(
        "SELECT COUNT(*) FROM transacoes WHERE user_id=%s AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s",
        (USER_ID, mes, ano)
    )[0]

    dias_com_gastos = _fetch_one(
        "SELECT COUNT(DISTINCT data_transacao) FROM transacoes WHERE tipo='gasto' AND user_id=%s AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s",
        (USER_ID, mes, ano)
    )[0]

    media_diaria = float(total_gastos) / max(dias_com_gastos, 1)

    categorias = _fetch(
        """SELECT c.nome, c.emoji, COALESCE(SUM(t.valor),0) as total
           FROM categorias c
           LEFT JOIN transacoes t ON t.categoria_id=c.id AND t.tipo='gasto' AND t.user_id=%s
               AND EXTRACT(MONTH FROM t.data_transacao)=%s AND EXTRACT(YEAR FROM t.data_transacao)=%s
           GROUP BY c.id, c.nome, c.emoji
           HAVING COALESCE(SUM(t.valor),0) > 0
           ORDER BY total DESC""",
        (USER_ID, mes, ano)
    )

    metas = _fetch(
        """SELECT c.nome, c.emoji, m.limite,
                  COALESCE(SUM(t.valor),0) as gasto
           FROM metas m
           JOIN categorias c ON c.id=m.categoria_id
           LEFT JOIN transacoes t ON t.categoria_id=m.categoria_id AND t.tipo='gasto' AND t.user_id=m.user_id
               AND EXTRACT(MONTH FROM t.data_transacao)=m.mes AND EXTRACT(YEAR FROM t.data_transacao)=m.ano
           WHERE m.mes=%s AND m.ano=%s AND m.user_id=%s
           GROUP BY c.nome, c.emoji, m.limite
           ORDER BY c.nome""",
        (mes, ano, USER_ID)
    )

    ultimas = _fetch(
        """SELECT t.tipo, t.valor, t.descricao, t.pagamento, t.data_transacao, c.nome, c.emoji, t.parcelas, b.nome
           FROM transacoes t
           LEFT JOIN categorias c ON c.id=t.categoria_id
           LEFT JOIN bancos b ON b.id=t.banco_id
           WHERE t.user_id=%s AND EXTRACT(MONTH FROM t.data_transacao)=%s AND EXTRACT(YEAR FROM t.data_transacao)=%s
           ORDER BY t.created_at DESC LIMIT 10""",
        (USER_ID, mes, ano)
    )

    meses_map = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    faturas_raw = _fetch(
        """SELECT b.nome,
                  COALESCE(SUM(t.valor),0) as total,
                  b.dia_fechamento,
                  b.limite
           FROM transacoes t
           JOIN bancos b ON b.id = t.banco_id
           WHERE t.user_id = %s AND t.tipo = 'gasto' AND t.pagamento = 'credito'
               AND t.banco_id IS NOT NULL
           GROUP BY b.nome, b.dia_fechamento, b.limite
           HAVING COALESCE(SUM(t.valor),0) > 0
           ORDER BY b.nome""",
        (USER_ID,)
    )
    faturas = [(nome, float(total), dia, float(limite) if limite else 0) for nome, total, dia, limite in faturas_raw]

    heatmap_raw = _fetch(
        """SELECT EXTRACT(DAY FROM data_transacao)::int, COALESCE(SUM(valor),0)
           FROM transacoes
           WHERE tipo='gasto' AND user_id=%s
               AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s
           GROUP BY EXTRACT(DAY FROM data_transacao)
           ORDER BY EXTRACT(DAY FROM data_transacao)""",
        (USER_ID, mes, ano)
    )
    heatmap = [(int(dia), float(val)) for dia, val in heatmap_raw]

    return templates.TemplateResponse(request, "dashboard.html", {
        "total_gastos": total_gastos,
        "total_rendas": total_rendas,
        "saldo": saldo,
        "gastos_hoje": gastos_hoje,
        "maior_gasto": maior_gasto,
        "total_transacoes": total_transacoes,
        "media_diaria": media_diaria,
        "categorias": categorias,
        "metas": metas,
        "ultimas": ultimas,
        "faturas": faturas,
        "heatmap": heatmap,
        "mes": mes,
        "ano": ano,
        "mes_nome": meses_map.get(mes, ""),
    })


@app.get("/transacoes", response_class=HTMLResponse)
async def transacoes(
    request: Request,
    mes: int = Query(default=None),
    ano: int = Query(default=None),
    tipo: str = Query(default=None),
):
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    where = "WHERE t.user_id=%s AND EXTRACT(MONTH FROM t.data_transacao)=%s AND EXTRACT(YEAR FROM t.data_transacao)=%s"
    params = [USER_ID, mes, ano]

    if tipo in ("gasto", "renda"):
        where += " AND t.tipo=%s"
        params.append(tipo)

    rows = _fetch(
        f"""SELECT t.id, t.tipo, t.valor, t.descricao, t.pagamento, t.data_transacao,
                   c.nome, c.emoji, t.parcelas, b.nome, t.created_at
            FROM transacoes t
            LEFT JOIN categorias c ON c.id=t.categoria_id
            LEFT JOIN bancos b ON b.id=t.banco_id
            {where}
            ORDER BY t.created_at DESC""",
        tuple(params)
    )

    meses_map = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    return templates.TemplateResponse(request, "transacoes.html", {
        "rows": rows,
        "mes": mes,
        "ano": ano,
        "mes_nome": meses_map.get(mes, ""),
        "tipo_filtro": tipo,
    })


@app.post("/transacoes/{transacao_id}/deletar")
async def deletar_transacao(transacao_id: int):
    _execute("DELETE FROM transacoes WHERE id=%s AND user_id=%s", (transacao_id, USER_ID))
    return RedirectResponse("/transacoes", status_code=303)


@app.get("/categorias", response_class=HTMLResponse)
async def categorias_page(request: Request):
    cats = _fetch(
        """SELECT c.id, c.nome, c.emoji, COUNT(t.id) as total_registros,
                  COALESCE(SUM(t.valor),0) as total_valor
           FROM categorias c
           LEFT JOIN transacoes t ON t.categoria_id=c.id AND t.user_id=%s
           GROUP BY c.id, c.nome, c.emoji
           ORDER BY c.nome""",
        (USER_ID,)
    )
    return templates.TemplateResponse(request, "categorias.html", {
        "categorias": cats,
    })


@app.post("/categorias/criar")
async def criar_categoria(nome: str = Form(...), emoji: str = Form(default=None)):
    _insert("INSERT INTO categorias (nome, emoji) VALUES (%s, %s)", (nome, emoji or None))
    return RedirectResponse("/categorias", status_code=303)


@app.post("/categorias/{cat_id}/deletar")
async def deletar_categoria(cat_id: int):
    _execute("DELETE FROM categorias WHERE id=%s", (cat_id,))
    return RedirectResponse("/categorias", status_code=303)


@app.get("/bancos", response_class=HTMLResponse)
async def bancos_page(request: Request):
    bancos = _fetch(
        """SELECT b.id, b.nome, b.dia_fechamento, b.limite,
                  COALESCE(SUM(t.valor),0) as total_gasto,
                  COUNT(t.id) as total_transacoes
           FROM bancos b
           LEFT JOIN transacoes t ON t.banco_id=b.id AND t.tipo='gasto' AND t.user_id=%s
               AND EXTRACT(MONTH FROM t.data_transacao)=EXTRACT(MONTH FROM CURRENT_DATE)
               AND EXTRACT(YEAR FROM t.data_transacao)=EXTRACT(YEAR FROM CURRENT_DATE)
           GROUP BY b.id, b.nome, b.dia_fechamento, b.limite
           ORDER BY b.nome""",
        (USER_ID,)
    )
    return templates.TemplateResponse(request, "bancos.html", {
        "bancos": bancos,
    })


@app.post("/bancos/criar")
async def criar_banco(nome: str = Form(...), dia_fechamento: int = Form(...), limite: float = Form(default=0)):
    _insert("INSERT INTO bancos (nome, dia_fechamento, limite) VALUES (%s, %s, %s)", (nome, dia_fechamento, limite))
    return RedirectResponse("/bancos", status_code=303)


@app.post("/bancos/{banco_id}/deletar")
async def deletar_banco(banco_id: int):
    _execute("DELETE FROM bancos WHERE id=%s", (banco_id,))
    return RedirectResponse("/bancos", status_code=303)


@app.get("/metas", response_class=HTMLResponse)
async def metas_page(request: Request, mes: int = Query(default=None), ano: int = Query(default=None)):
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    metas = _fetch(
        """SELECT m.id, c.nome, c.emoji, m.limite,
                  COALESCE(SUM(t.valor),0) as gasto
           FROM metas m
           JOIN categorias c ON c.id=m.categoria_id
           LEFT JOIN transacoes t ON t.categoria_id=m.categoria_id AND t.tipo='gasto' AND t.user_id=m.user_id
               AND EXTRACT(MONTH FROM t.data_transacao)=m.mes AND EXTRACT(YEAR FROM t.data_transacao)=m.ano
           WHERE m.mes=%s AND m.ano=%s AND m.user_id=%s
           GROUP BY c.nome, c.emoji, m.limite, m.id
           ORDER BY c.nome""",
        (mes, ano, USER_ID)
    )

    categorias = _fetch("SELECT id, nome, emoji FROM categorias ORDER BY nome")

    meses_map = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    return templates.TemplateResponse(request, "metas.html", {
        "metas": metas,
        "categorias": categorias,
        "mes": mes,
        "ano": ano,
        "mes_nome": meses_map.get(mes, ""),
    })


@app.post("/metas/criar")
async def criar_meta(categoria_id: int = Form(...), mes: int = Form(...), ano: int = Form(...), limite: float = Form(...)):
    _execute(
        """INSERT INTO metas (categoria_id, mes, ano, limite, user_id)
           VALUES (%s, %s, %s, %s, %s)
           ON CONFLICT (categoria_id, mes, ano, user_id)
           DO UPDATE SET limite = EXCLUDED.limite""",
        (categoria_id, mes, ano, limite, USER_ID)
    )
    return RedirectResponse(f"/metas?mes={mes}&ano={ano}", status_code=303)


@app.post("/metas/{meta_id}/deletar")
async def deletar_meta(meta_id: int, mes: int = Query(default=7), ano: int = Query(default=2026)):
    _execute("DELETE FROM metas WHERE id=%s AND user_id=%s", (meta_id, USER_ID))
    return RedirectResponse(f"/metas?mes={mes}&ano={ano}", status_code=303)


@app.get("/fixos", response_class=HTMLResponse)
async def fixos_page(request: Request):
    fixos = _fetch(
        """SELECT f.id, f.tipo, f.valor, f.descricao, f.pagamento, f.parcelas, f.dia, f.ativo,
                  c.nome, c.emoji, b.nome
           FROM fixos f
           LEFT JOIN categorias c ON c.id = f.categoria_id
           LEFT JOIN bancos b ON b.id = f.banco_id
           WHERE f.user_id = %s
           ORDER BY f.tipo, f.dia""",
        (USER_ID,)
    )
    categorias = _fetch("SELECT id, nome, emoji FROM categorias ORDER BY nome")
    bancos = _fetch("SELECT id, nome FROM bancos ORDER BY nome")
    return templates.TemplateResponse(request, "fixos.html", {
        "fixos": fixos,
        "categorias": categorias,
        "bancos": bancos,
    })


@app.post("/fixos/criar")
async def criar_fixo(
    tipo: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...),
    dia: int = Form(default=1),
    pagamento: str = Form(default="debito"),
    categoria_id: int = Form(default=None),
    banco_id: int = Form(default=None),
    parcelas: int = Form(default=1),
):
    _insert(
        """INSERT INTO fixos (tipo, valor, descricao, pagamento, user_id, categoria_id, banco_id, parcelas, dia)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (tipo, valor, descricao, pagamento, USER_ID, categoria_id or None, banco_id or None, parcelas, dia)
    )
    return RedirectResponse("/fixos", status_code=303)


@app.post("/fixos/{fixo_id}/deletar")
async def deletar_fixo(fixo_id: int):
    _execute("DELETE FROM fixos WHERE id=%s AND user_id=%s", (fixo_id, USER_ID))
    return RedirectResponse("/fixos", status_code=303)


@app.post("/fixos/{fixo_id}/toggle")
async def toggle_fixo(fixo_id: int):
    _execute("UPDATE fixos SET ativo = NOT ativo WHERE id=%s AND user_id=%s", (fixo_id, USER_ID))
    return RedirectResponse("/fixos", status_code=303)


@app.get("/api/gastos_por_categoria")
async def api_gastos_por_categoria(mes: int, ano: int):
    rows = _fetch(
        """SELECT c.emoji || ' ' || c.nome, COALESCE(SUM(t.valor),0)
           FROM categorias c
           LEFT JOIN transacoes t ON t.categoria_id=c.id AND t.tipo='gasto' AND t.user_id=%s
               AND EXTRACT(MONTH FROM t.data_transacao)=%s AND EXTRACT(YEAR FROM t.data_transacao)=%s
           GROUP BY c.id, c.nome, c.emoji
           HAVING COALESCE(SUM(t.valor),0) > 0
           ORDER BY SUM(t.valor) DESC""",
        (USER_ID, mes, ano)
    )
    return {"labels": [r[0] for r in rows], "values": [float(r[1]) for r in rows]}


@app.get("/api/gastos_por_dia")
async def api_gastos_por_dia(mes: int, ano: int):
    rows = _fetch(
        """SELECT EXTRACT(DAY FROM data_transacao)::int, COALESCE(SUM(valor),0)
           FROM transacoes
           WHERE tipo='gasto' AND user_id=%s
               AND EXTRACT(MONTH FROM data_transacao)=%s AND EXTRACT(YEAR FROM data_transacao)=%s
           GROUP BY EXTRACT(DAY FROM data_transacao)
           ORDER BY EXTRACT(DAY FROM data_transacao)""",
        (USER_ID, mes, ano)
    )
    return {"labels": [r[0] for r in rows], "values": [float(r[1]) for r in rows]}
