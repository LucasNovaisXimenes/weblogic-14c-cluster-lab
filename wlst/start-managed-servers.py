"""
start-managed-servers.py — Inicia ms1 e ms2 via AdminServer.

Usa start('msX', 'Server') que carrega configuração do config.xml e delega
ao Node Manager. É o fluxo canônico — não usar nmStart() diretamente.
"""
import sys
execfile('/u01/wlst/common.py')

SERVERS = ['ms1', 'ms2']


def main():
    for name in SERVERS:
        log('Iniciando %s...' % name)
        try:
            state = serverRuntime(name).getState()
            if state == 'RUNNING':
                log('%s já está RUNNING.' % name)
                continue
        except Exception:
            pass

        start(name, 'Server', block='true')
        log('%s iniciado.' % name)


connect_admin()
main()
disconnect_admin()
