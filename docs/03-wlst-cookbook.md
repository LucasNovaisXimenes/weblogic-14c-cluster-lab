# WLST Cookbook — Operação Diária do WebLogic Lab

Snippets prontos para as operações mais comuns via WLST. Todos assumem que o AdminServer está rodando e as variáveis de ambiente estão configuradas.

## Como conectar

```bash
# Na VM, como usuário ubuntu
export WL_ADMIN_USER=weblogic
export WL_ADMIN_PASSWORD='Welcome1#Lab'
export WL_ADMIN_URL='t3://localhost:7001'

cd /u01/app/oracle/middleware/oracle_common/common/bin
./wlst.sh
```

---

## Servidores

### Listar todos os servers e estado

```python
connect('weblogic', 'Welcome1#Lab', 't3://localhost:7001')
domainConfig()
servers = cmo.getServers()
for s in servers:
    name = s.getName()
    try:
        cd('/ServerLifeCycleRuntimes/' + name)
        state = cmo.getState()
    except:
        state = 'N/A'
    print('%s -> %s' % (name, state))
```

### Iniciar um Managed Server

```python
# Via AdminServer (canônico — usa Node Manager)
start('ms1', 'Server', block='true')
```

### Parar um Managed Server graciosamente

```python
shutdown('ms1', 'Server', ignoreSessions='false', timeOut=60, block='true')
```

### Parar forçado (kill)

```python
shutdown('ms1', 'Server', ignoreSessions='true', force='true', block='true')
```

### Ver linha de comando da JVM de um server

```python
serverRuntime('ms1')
cd('/ServerRuntimes/ms1')
print(cmo.getJVMArgs())
```

---

## Data Sources

### Listar Data Sources e estado do pool

```python
domainRuntime()
cd('/ServerRuntimes/ms1/JDBCServiceRuntime/ms1/JDBCDataSourceRuntimeMBeans/LabDS')
print('Active:    ', cmo.getActiveConnectionsCurrentCount())
print('Available: ', cmo.getNumAvailable())
print('Leaked:    ', cmo.getConnectionLeakCurrentCount())
print('Waiters:   ', cmo.getWaitingForConnectionCurrentCount())
```

### Testar conexão do Data Source

```python
domainRuntime()
cd('/ServerRuntimes/ms1/JDBCServiceRuntime/ms1/JDBCDataSourceRuntimeMBeans/LabDS')
result = cmo.testPool()
if result is None:
    print('Pool OK')
else:
    print('Falha: ' + result)
```

### Resetar pool (fecha todas as conexões e reabre)

```python
domainRuntime()
cd('/ServerRuntimes/ms1/JDBCServiceRuntime/ms1/JDBCDataSourceRuntimeMBeans/LabDS')
cmo.reset()
```

---

## Deploy

### Status de todas as aplicações

```python
domainConfig()
apps = cmo.getAppDeployments()
for app in apps:
    print(app.getName(), '->', app.getTargets())
```

### Redeploy de um WAR já deployado

```python
# Requer que o app esteja em estado ACTIVE
redeploy(
    appName = 'hello',
    path    = '/u01/stage/hello.war',
    block   = 'true',
)
```

### Undeploy + deploy limpo

```python
stopApplication('hello')
undeploy('hello', targets='cluster1')
deploy(
    appName   = 'hello',
    path      = '/u01/stage/hello.war',
    targets   = 'cluster1',
    stageMode = 'stage',
    block     = 'true',
)
```

---

## Cluster

### Ver membros do cluster e estado

```python
domainRuntime()
cd('/DomainRuntime/ServerLifeCycleRuntimes')
ls()
# Para cada MS:
cd('/DomainRuntime/ServerLifeCycleRuntimes/ms1')
print(cmo.getState())
```

### Ver estatísticas de request do cluster

```python
serverRuntime('ms1')
cd('/ServerRuntimes/ms1/ClusterRuntime')
print('Primaries:    ', cmo.getPrimaryCount())
print('Secondaries:  ', cmo.getSecondaryCount())
```

---

## Configuração do domínio

### Alterar parâmetro de um server (exemplo: heap JVM)

```python
edit()
startEdit()
cd('/Servers/ms1/ServerStart/ms1')
args = get('Arguments') or ''
if '-Xmx' not in args:
    set('Arguments', args + ' -Xmx2048m -Xms512m')
save()
activate(block='true')
# O server precisa ser reiniciado para o argumento ter efeito
```

### Ver e alterar timeout de transação global

```python
edit()
startEdit()
cd('/JTA/base_domain')
print('Timeout atual:', get('TimeoutSeconds'))
set('TimeoutSeconds', 60)
save()
activate(block='true')
```

---

## Node Manager

### Ver log do Node Manager em tempo real

```bash
tail -f /u01/app/oracle/domains/base_domain/nodemanager/nodemanager.log
```

### Verificar que NM está aceitando conexões

```bash
nc -z localhost 5556 && echo "NM UP" || echo "NM DOWN"
```

### Reconectar o AdminServer ao Node Manager (se conexão cair)

```python
# Não é necessário reiniciar o AdminServer — ele reconecta automaticamente.
# Em último caso, reinicie o serviço:
# systemctl restart weblogic-nodemanager
```

---

## Derby (banco de demo)

### Conectar via CLI ij

```bash
chmod +x /u01/app/oracle/middleware/wlserver/common/derby/bin/ij
/u01/app/oracle/middleware/wlserver/common/derby/bin/ij

ij> connect 'jdbc:derby://localhost:1527/labdb';
ij> SELECT * FROM funcionarios;
ij> quit;
```

### Verificar que o Derby Network Server está rodando

```bash
/u01/app/oracle/middleware/wlserver/common/derby/bin/NetworkServerControl ping \
  -h localhost -p 1527
```

---

## Diagnóstico rápido

### Sequência de logs quando um MS não sobe

```
1. /u01/app/oracle/domains/base_domain/nodemanager/nodemanager.log
   → Confirma que NM recebeu o comando start e o resultado

2. /u01/app/oracle/domains/base_domain/servers/ms1/logs/ms1.out
   → Stack trace real da JVM do MS — aqui está a causa raiz

3. /u01/app/oracle/domains/base_domain/servers/ms1/logs/ms1.log
   → Logs de runtime após boot (transações, deploys, etc.)
```

### Verificar linha de comando Java do processo MS

```bash
# Na VM
ps aux | grep ms1
# Ou, mais limpo:
cat /proc/$(pgrep -f weblogic.Name=ms1)/cmdline | tr '\0' '\n'
```
