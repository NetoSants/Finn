from .start import start
from .help import help_command
from .gasto import gasto, gasto_callback
from .renda import renda, renda_text
from .saldo import saldo
from .extrato import extrato
from .ping import ping
from .bancos import bancos, bancos_callback, banco_text
from .parcelas import parcelas, parcelar
from .meta import meta
from .categorias import categorias

from .menu import menu_callback
from .ajuda import ajuda_callback
from .resumo import resumo
from .exportar import exportar

COMMANDS = {
    "start": start,
    "help": help_command,
    "gasto": gasto,
    "renda": renda,
    "saldo": saldo,
    "extrato": extrato,
    "ping": ping,
    "bancos": bancos,
    "parcelas": parcelas,
    "parcelar": parcelar,
    "meta": meta,
    "categorias": categorias,
    "resumo": resumo,
    "exportar": exportar,
}

CALLBACKS = [
    ("^menu_", menu_callback),
    ("^ajuda_", ajuda_callback),
    ("^gasto_", gasto_callback),
    ("^bancos_", bancos_callback),
]
