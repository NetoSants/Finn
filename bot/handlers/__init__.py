from .start import start
from .help import help_command
from .gasto import gasto, gasto_callback
from .renda import renda
from .saldo import saldo
from .extrato import extrato
from .ping import ping
from .bancos import bancos, bancos_callback
from .cadastrar_banco import cadastrar_banco
from .remover_banco import remover_banco
from .parcelas import parcelas, parcelar
from .generic import ai_confirmar_callback, ai_cancelar_callback, pag_callback

COMMANDS = {
    "start": start,
    "help": help_command,
    "gasto": gasto,
    "renda": renda,
    "saldo": saldo,
    "extrato": extrato,
    "ping": ping,
    "bancos": bancos,
    "cadastrar_banco": cadastrar_banco,
    "remover_banco": remover_banco,
    "parcelas": parcelas,
    "parcelar": parcelar,
}

CALLBACKS = [
    ("^gasto_", gasto_callback),
    ("^bancos_", bancos_callback),
    ("^pag_", pag_callback),
    ("^ai_confirmar$", ai_confirmar_callback),
    ("^ai_cancelar$", ai_cancelar_callback),
]
