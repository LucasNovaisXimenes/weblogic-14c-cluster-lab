"""
04-create-cluster.py — Cria cluster1 e adiciona ms1 e ms2 como membros.
"""
import sys
execfile('/u01/wlst/common.py')

CLUSTER_NAME = 'cluster1'
MEMBERS      = ['ms1', 'ms2']


def main():
    ensure_edit()

    if not mbean_exists('/Clusters/' + CLUSTER_NAME):
        log('Criando cluster: ' + CLUSTER_NAME)
        cd('/')
        cmo.createCluster(CLUSTER_NAME)

        cd('/Clusters/' + CLUSTER_NAME)
        set('MulticastAddress', '239.192.0.0')
        set('MulticastPort',    7777)
        set('ClusterMessagingMode', 'unicast')
    else:
        log('Cluster %s já existe.' % CLUSTER_NAME)

    for ms_name in MEMBERS:
        cd('/Servers/' + ms_name)
        current_cluster = get('Cluster')
        if current_cluster is None:
            log('Adicionando %s ao cluster %s...' % (ms_name, CLUSTER_NAME))
            set('Cluster', getMBean('/Clusters/' + CLUSTER_NAME))
        else:
            log('%s já está no cluster.' % ms_name)

    save_activate()
    log('Cluster %s configurado com membros: %s' % (CLUSTER_NAME, ', '.join(MEMBERS)))


connect_admin()
main()
disconnect_admin()
