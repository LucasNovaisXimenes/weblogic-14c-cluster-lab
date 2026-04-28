"""
99-destroy-domain.py — Para todos os servers e remove os arquivos do domínio.

Modo misto: tenta parar servers via AdminServer (online). Se o Admin não
responder, mata processos e remove arquivos diretamente (offline).
"""
import os
import sys
import shutil
execfile('/u01/wlst/common.py')

SERVERS_TO_STOP = ['ms1', 'ms2']


def stop_servers_online():
    log('Parando Managed Servers via AdminServer...')
    for name in SERVERS_TO_STOP:
        try:
            log('Parando %s...' % name)
            shutdown(name, 'Server', ignoreSessions='true', timeOut=30, block='true')
            log('%s parado.' % name)
        except Exception as e:
            log('Aviso ao parar %s: %s' % (name, str(e)))

    log('Parando AdminServer...')
    try:
        shutdown('AdminServer', 'Server', ignoreSessions='true', timeOut=30, block='true')
    except Exception as e:
        log('Aviso ao parar AdminServer: %s' % str(e))


def remove_domain_files():
    if os.path.exists(DOMAIN_PATH):
        log('Removendo diretório do domínio: ' + DOMAIN_PATH)
        shutil.rmtree(DOMAIN_PATH)
        log('Domínio removido.')
    else:
        log('Diretório do domínio não encontrado: ' + DOMAIN_PATH)


def main():
    log('=== Destruindo domínio base_domain ===')

    try:
        connect_admin()
        stop_servers_online()
        disconnect_admin()
    except Exception as e:
        log('Não foi possível conectar ao AdminServer: %s' % str(e))
        log('Prosseguindo com remoção dos arquivos...')

    remove_domain_files()
    log('=== Domínio destruído ===')


main()
