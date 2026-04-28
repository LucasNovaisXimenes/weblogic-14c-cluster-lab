"""
03-create-managed-servers.py — Cria ms1 e ms2, associa à Machine LocalMachine.

Associar à Machine é obrigatório para que o AdminServer saiba como se conectar
ao Node Manager para iniciar/parar esses servidores.
"""
import sys
execfile('/u01/wlst/common.py')

MANAGED_SERVERS = [
    {'name': 'ms1', 'port': 8001},
    {'name': 'ms2', 'port': 8002},
]


def create_server(name, port):
    if mbean_exists('/Servers/' + name):
        log('Servidor %s já existe. Pulando.' % name)
        return

    log('Criando Managed Server: %s (porta %d)...' % (name, port))
    cd('/')
    cmo.createServer(name)

    cd('/Servers/' + name)
    set('ListenAddress', 'localhost')
    set('ListenPort',    port)
    set('Machine',       getMBean('/Machines/LocalMachine'))

    # Gera startup.properties com AdminURL correto (t3, não http)
    cd('/Servers/' + name + '/ServerStart/' + name)
    set('Arguments',    '-Dweblogic.management.server=t3://localhost:7001')

    log('Servidor %s criado.' % name)


def main():
    ensure_edit()

    for ms in MANAGED_SERVERS:
        create_server(ms['name'], ms['port'])

    save_activate()
    log('Managed Servers configurados.')


connect_admin()
main()
disconnect_admin()
