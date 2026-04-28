"""
05-create-datasource.py — Cria o Data Source LabDS apontando para o Derby embutido.

Usa Generic DS (não-XA) para evitar overhead de Two-Phase Commit no lab.
O Derby Network Server roda na porta 1527, criado automaticamente pelo WebLogic.
"""
import sys
execfile('/u01/wlst/common.py')

DS_NAME    = 'LabDS'
DS_JNDI    = 'jdbc/LabDS'
CLUSTER    = 'cluster1'
DB_NAME    = 'labdb'
DERBY_PORT = 1527

# Driver Derby não-XA (Generic DS)
DRIVER_CLASS = 'org.apache.derby.jdbc.ClientDriver'
CONN_URL     = 'jdbc:derby://localhost:%d/%s;create=true' % (DERBY_PORT, DB_NAME)

POOL_MIN  = 1
POOL_MAX  = 15
POOL_INIT = 1


def main():
    # Verifica se DS já existe
    if mbean_exists('/JDBCSystemResources/' + DS_NAME):
        log('Data Source %s já existe. Nada a fazer.' % DS_NAME)
        return

    log('Criando Data Source: %s -> %s' % (DS_NAME, CONN_URL))
    ensure_edit()

    cd('/')
    cmo.createJDBCSystemResource(DS_NAME)

    cd('/JDBCSystemResources/%s/JDBCResource/%s' % (DS_NAME, DS_NAME))
    set('Name', DS_NAME)

    # Configuração do driver
    cd('/JDBCSystemResources/%s/JDBCResource/%s/JDBCDriverParams/%s' % (DS_NAME, DS_NAME, DS_NAME))
    set('DriverName', DRIVER_CLASS)
    set('URL',        CONN_URL)
    set('PasswordEncrypted', '')

    # Connection Pool
    cd('/JDBCSystemResources/%s/JDBCResource/%s/JDBCConnectionPoolParams/%s' % (DS_NAME, DS_NAME, DS_NAME))
    set('MinCapacity',     POOL_MIN)
    set('MaxCapacity',     POOL_MAX)
    set('InitialCapacity', POOL_INIT)
    set('TestConnectionsOnReserve', True)
    set('TestTableName',  'SQL SELECT 1 FROM SYS.SYSTABLES')

    # JNDI
    cd('/JDBCSystemResources/%s/JDBCResource/%s/JDBCDataSourceParams/%s' % (DS_NAME, DS_NAME, DS_NAME))
    set('JNDINames', jarray.array([String(DS_JNDI)], String))
    set('GlobalTransactionsProtocol', 'None')

    # Target: cluster1
    cd('/JDBCSystemResources/' + DS_NAME)
    set('Targets', jarray.array([getMBean('/Clusters/' + CLUSTER)], ObjectName))

    save_activate()
    log('Data Source %s criado e targetado no cluster %s.' % (DS_NAME, CLUSTER))

    # Inicializa a tabela de demo (ignora se já existe)
    _init_demo_table()


def _init_demo_table():
    """Cria e popula a tabela funcionarios no Derby via JDBC."""
    import java.sql
    import javax.naming

    log('Inicializando tabela "funcionarios" no Derby...')
    try:
        ctx  = javax.naming.InitialContext()
        ds   = ctx.lookup(DS_JNDI)
        conn = ds.getConnection()
        stmt = conn.createStatement()

        try:
            stmt.execute("""
                CREATE TABLE funcionarios (
                    id    INT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nome  VARCHAR(100),
                    cargo VARCHAR(100)
                )
            """)
            log('Tabela criada.')
        except Exception:
            log('Tabela já existe, pulando criação.')

        dados = [
            ("Ana Lima",    "WebLogic Admin"),
            ("Bruno Costa", "Java Developer"),
            ("Carla Souza", "DBA Oracle"),
        ]
        for nome, cargo in dados:
            try:
                stmt.execute(
                    "INSERT INTO funcionarios (nome, cargo) VALUES ('%s', '%s')" % (nome, cargo)
                )
            except Exception:
                pass

        conn.close()
        log('Tabela inicializada.')
    except Exception as e:
        log('Aviso ao inicializar tabela (pode ser normal se DS ainda não estiver ativo): ' + str(e))


connect_admin()
main()
disconnect_admin()
