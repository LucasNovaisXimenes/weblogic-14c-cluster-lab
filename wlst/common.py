"""
Utilitários compartilhados para todos os scripts WLST do lab.
Importado com: execfile('/u01/wlst/common.py')
"""
import os
import sys

# Lê variáveis de ambiente com fallback
ADMIN_USER     = os.environ.get('WL_ADMIN_USER',     'weblogic')
ADMIN_PASSWORD = os.environ.get('WL_ADMIN_PASSWORD', 'Welcome1#Lab')
ADMIN_URL      = os.environ.get('WL_ADMIN_URL',      't3://localhost:7001')
DOMAIN_PATH    = os.environ.get('WL_DOMAIN_PATH',    '/u01/app/oracle/domains/base_domain')
MW_HOME        = os.environ.get('WL_MIDDLEWARE_HOME', '/u01/app/oracle/middleware')


def log(msg):
    print('[WLST] ' + str(msg))
    sys.stdout.flush()


def connect_admin():
    """Conecta no AdminServer e vai para serverConfig."""
    log('Conectando em %s como %s...' % (ADMIN_URL, ADMIN_USER))
    connect(ADMIN_USER, ADMIN_PASSWORD, ADMIN_URL)
    log('Conectado.')


def disconnect_admin():
    """Desconecta com segurança."""
    try:
        disconnect()
    except Exception:
        pass


def mbean_exists(path):
    """
    Retorna True se o MBean no path dado existir.
    Exemplo: mbean_exists('/Servers/ms1')
    """
    try:
        cd(path)
        return True
    except Exception:
        return False


def ensure_edit():
    """Entra em modo de edição se ainda não estiver."""
    try:
        edit()
        startEdit()
    except Exception as e:
        log('Aviso ao entrar em edição: %s' % str(e))


def save_activate():
    """Salva e ativa as mudanças."""
    save()
    activate(block='true')
    log('Mudanças ativadas.')


def run_script(func):
    """
    Decorator de conveniência: conecta, roda func, desconecta.
    Uso: run_script(minha_funcao)
    """
    try:
        connect_admin()
        func()
    except Exception as e:
        log('ERRO: %s' % str(e))
        sys.exit(1)
    finally:
        disconnect_admin()
