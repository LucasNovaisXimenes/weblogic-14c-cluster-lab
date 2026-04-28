"""
02-create-machine.py — Cria a Machine LocalMachine no domínio (modo online).

A Machine é o MBean que representa um host físico e guarda os parâmetros
de conexão com o Node Manager daquele host. Sem ela, o AdminServer não sabe
onde o NM está e Managed Servers não iniciam via start('msX','Server').
"""
import sys
execfile('/u01/wlst/common.py')


def main():
    if mbean_exists('/Machines/LocalMachine'):
        log('Machine LocalMachine já existe. Nada a fazer.')
        return

    log('Criando Machine LocalMachine...')
    ensure_edit()

    cd('/')
    cmo.createUnixMachine('LocalMachine')

    cd('/Machines/LocalMachine/NodeManager/LocalMachine')
    set('NMType',        'Plain')
    set('ListenAddress', 'localhost')
    set('ListenPort',    5556)

    save_activate()
    log('Machine LocalMachine criada.')


connect_admin()
main()
disconnect_admin()
