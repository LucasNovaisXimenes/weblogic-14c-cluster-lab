"""
06-deploy-app.py — Deploy do WAR hello no cluster1.

Se a aplicação já existir, faz undeploy e redeploy (redeploy direto pode
deixar artefatos antigos se o WAR mudou muito).
"""
import os
import sys
execfile('/u01/wlst/common.py')

APP_NAME    = os.environ.get('WL_APP_NAME',    'hello')
APP_WAR     = os.environ.get('WL_APP_WAR',     '/u01/stage/hello.war')
CLUSTER     = os.environ.get('WL_CLUSTER_NAME','cluster1')


def main():
    log('Deploy de %s -> cluster %s' % (APP_WAR, CLUSTER))

    if not os.path.exists(APP_WAR):
        log('ERRO: WAR não encontrado em ' + APP_WAR)
        sys.exit(1)

    # Verifica se app já está deployada
    existing = None
    try:
        cd('/AppDeployments/' + APP_NAME)
        existing = True
    except Exception:
        existing = False

    if existing:
        log('Aplicação %s já existe. Fazendo undeploy...' % APP_NAME)
        stopApplication(APP_NAME)
        undeploy(APP_NAME, targets=CLUSTER)

    log('Iniciando deploy...')
    deploy(
        appName    = APP_NAME,
        path       = APP_WAR,
        targets    = CLUSTER,
        stageMode  = 'stage',
        block      = 'true',
    )
    log('Deploy concluído. Aplicação disponível em /hello/')


connect_admin()
main()
disconnect_admin()
