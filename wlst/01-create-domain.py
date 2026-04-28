"""
01-create-domain.py — Cria o domínio base_domain em modo OFFLINE.

Modo offline: edita config.xml diretamente via readTemplate/writeDomain.
O AdminServer não precisa estar rodando.
"""
import os
import sys

ADMIN_USER     = os.environ.get('WL_ADMIN_USER',     'weblogic')
ADMIN_PASSWORD = os.environ.get('WL_ADMIN_PASSWORD', 'Welcome1#Lab')
DOMAIN_PATH    = os.environ.get('WL_DOMAIN_PATH',    '/u01/app/oracle/domains/base_domain')
MW_HOME        = os.environ.get('WL_MIDDLEWARE_HOME', '/u01/app/oracle/middleware')

TEMPLATE_JAR = MW_HOME + '/wlserver/common/templates/wls/wls.jar'


def log(msg):
    print('[01-create-domain] ' + str(msg))
    sys.stdout.flush()


def main():
    log('Iniciando criação do domínio em: ' + DOMAIN_PATH)

    # Se o domínio já existe, encerra sem fazer nada (idempotência)
    if os.path.exists(DOMAIN_PATH + '/config/config.xml'):
        log('Domínio já existe. Nada a fazer.')
        return

    log('Carregando template: ' + TEMPLATE_JAR)
    readTemplate(TEMPLATE_JAR)

    # Configura AdminServer — Listen Address explícito para evitar
    # que o AdminURL no startup.properties saia como 0.0.0.0
    cd('/Servers/AdminServer')
    set('ListenAddress', 'localhost')
    set('ListenPort', 7001)

    # Configura credenciais do domínio
    cd('/Security/base_domain/User/weblogic')
    cmo.setName(ADMIN_USER)
    cmo.setPassword(ADMIN_PASSWORD)

    # Configura Node Manager em modo Plain (sem SSL no lab)
    cd('/NMProperties')
    set('NodeManagerType', 'Plain')
    set('ListenAddress', 'localhost')
    set('ListenPort', 5556)
    set('StartScriptEnabled', 'true')
    set('StartScriptName', 'startWebLogic.sh')
    set('LogLevel', 'INFO')

    log('Escrevendo domínio em: ' + DOMAIN_PATH)
    setOption('OverwriteDomain', 'true')
    writeDomain(DOMAIN_PATH)
    closeTemplate()

    log('Domínio criado com sucesso.')


main()
