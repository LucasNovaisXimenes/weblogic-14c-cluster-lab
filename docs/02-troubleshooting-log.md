# Troubleshooting Log

Problemas reais enfrentados ao construir este lab, com causa-raiz e solução. Esta documentação prioriza **raciocínio por camadas** sobre receita — o objetivo é demonstrar metodologia de análise de incidentes em WebLogic.

---

## #1 — Managed Server não inicia: "Booting as admin server"

### Sintoma

Ao executar `nmStart('ms1')` via WLST, o Node Manager retorna erro genérico:

```
Server start command for WebLogic server 'ms1' failed due to:
[Server failed to start up but Node Manager was not aware of the reason].
```

### Investigação

O log do Node Manager (`nodemanager.log`) só confirma a falha sem apontar causa. A pista real está no `ms1.out` do próprio Managed Server:

```
weblogic.management.ManagementException:
Booting as admin server, but servername, ms1,
does not match the admin server name, AdminServer
```

### Causa-raiz

Três camadas de problema, descobertas sequencialmente:

**Camada 1 — `AdminURL` inválido no `startup.properties`:**

O `nmGenBootStartupProps()` gerou o arquivo com:

```properties
AdminURL=http://0.0.0.0:7001
```

Dois erros aqui:

- Protocolo `http` em vez de `t3`. Managed Server se comunica com AdminServer via T3 (protocolo proprietário do WebLogic sobre TCP). HTTP não serve para o handshake de management.
- `0.0.0.0` é endereço de *bind* (escutar em todas as interfaces), não de *conexão*. Como endereço de client é inválido.

Com `AdminURL` quebrado, o `ms1` não conseguia puxar sua configuração do AdminServer. Sem configuração, o WebLogic cai num fallback: tenta bootar como AdminServer standalone. Aí compara o próprio nome (`ms1`) com o nome do AdminServer (`AdminServer`) no `config.xml`, não bate, e morre.

**Por que o AdminURL saiu errado:** o AdminServer foi configurado com Listen Address vazio. Quando vazio, o WebLogic serializa como `0.0.0.0`, e o WLST pegou esse valor para gerar o `startup.properties`.

**Camada 2 — `startup.properties` corrigido não estava sendo lido:**

Mesmo após corrigir o arquivo, o erro persistia. Análise da linha de comando registrada no `ms1.out` mostrou que a JVM era executada **sem** o parâmetro `-Dweblogic.management.server`. Ou seja: o Node Manager não estava lendo o `startup.properties` corrigido.

Motivo: `nmStart('ms1')` puro via `nmConnect()` não lê o arquivo do disco — espera receber as propriedades explicitamente como argumento. O fluxo canônico é via AdminServer com `start('ms1','Server')`, que carrega tudo do `config.xml` e passa ao Node Manager.

**Camada 3 — AdminServer sem saber onde está o Node Manager:**

Ao mudar para `start('ms1','Server')`, novo erro:

```
Connection refused. Could not connect to NodeManager. Check that it is running at /0.0.0.0:5556.
```

Não existia objeto **Machine** no domínio, e o `ms1` não estava associado a nenhum. A Machine é o MBean que representa um host físico/virtual e **contém os parâmetros de conexão com o Node Manager daquele host** (tipo, endereço, porta). Sem Machine, o AdminServer não tinha informação e tentava `0.0.0.0:5556` por fallback.

### Solução

1. Ajustar `Listen Address` do AdminServer para `localhost` (previne regeneração incorreta do `AdminURL`)
2. Reescrever `startup.properties` com `AdminURL=t3://localhost:7001`
3. Criar Machine `LocalMachine` com NMType `Plain`, ListenAddress `localhost`, ListenPort `5556`
4. Associar `ms1` e `ms2` à Machine via `setMachine()`
5. Usar `start('msX','Server')` via AdminServer em vez de `nmStart()` direto

Após aplicar as correções:

```
wls:/base_domain/serverConfig/> start('ms1','Server')
Starting server ms1 ..............
Server with name ms1 started successfully
```

### Lições

- Erros "Node Manager was not aware of the reason" são **genéricos por design** — a análise real vai no `<server>.out` do Managed Server.
- WebLogic tem **três canais distintos** que precisam estar coerentes: config do domínio (`config.xml`), config do Node Manager (`nodemanager.properties` + `startup.properties` do server) e config da Machine (que amarra os dois).
- Sempre use `start('server','Server')` via AdminServer em operação normal. `nmStart()` é para cenários de disaster recovery quando o Admin está fora.
- Listen Address vazio em componentes WebLogic é uma **armadilha silenciosa** — sempre configure explicitamente.

---

## #2 — Data Source com driver XA inesperado

### Sintoma

Após criar Generic Data Source para Derby, o console mostra:

```
JDBC Driver: org.apache.derby.jdbc.ClientXADataSource
```

Esperava-se o driver não-XA (`ClientDataSource`).

### Causa-raiz

Na tela de "Transaction Options" do wizard, ao deixar **"Supports Global Transactions"** marcado (default), o WebLogic seleciona automaticamente o driver XA do banco, porque transações globais requerem suporte a Two-Phase Commit.

### Análise

Não é um erro — é comportamento esperado. Mas vale entender as implicações:

| Modo | Driver | Quando usar |
|---|---|---|
| Sem global transactions | `ClientDataSource` | App simples, só um recurso (um banco) |
| One-Phase Commit | `ClientDataSource` (ou XA) | App JTA mas com um único recurso — o WebLogic otimiza |
| Two-Phase Commit (XA) | `ClientXADataSource` | Múltiplos recursos em uma transação (banco + JMS, 2 bancos) |

Para o lab, XA é inofensivo. Em produção, escolha com base no que a aplicação realmente precisa — XA tem overhead de coordenação.

### Lição

Leia cada checkbox do wizard. "Supports Global Transactions" sozinho já muda o driver selecionado no passo seguinte. Entender essa cadeia evita surpresas em dimensionamento de performance.

---

## #3 — `ij.sh` não existe; `ij` sem permissão de execução

### Sintoma

Ao tentar usar o CLI do Derby:

```bash
./ij.sh
-bash: ./ij.sh: No such file or directory
```

### Investigação

Listagem do diretório mostra:

```
-rwxr-x--- startNetworkServer.sh
-rw-r----- ij                      ← sem bit de execução
```

Existem duas versões: o shell script `.sh` (não existe para `ij` nesta distribuição) e o binário sem extensão (existe, mas sem permissão de execução).

### Causa-raiz

Durante a instalação, o arquivo `ij` foi copiado sem preservar as permissões de execução.

### Solução

```bash
chmod +x /u01/app/oracle/middleware/wlserver/common/derby/bin/ij
./ij
```

### Lição

Vale como **item de checklist de pós-instalação do WebLogic**: após o Quick Installer, validar permissões de execução dos binários em `wlserver/common/derby/bin/` e `wlserver/server/bin/`. Em automação com Ansible, isso vira uma task `file: mode=0755` explícita.

---

## Metodologia geral

Um padrão que emerge dos problemas acima e que aplico sistematicamente:

1. **O erro reportado na camada externa (WLST, cliente) é quase sempre genérico.** A causa real está em logs internos do processo que falhou.
2. **Seguir a cadeia de logs na ordem:** ação do cliente → `nodemanager.log` → `<server>.out` → `<server>.log`. Cada camada dá mais contexto.
3. **Verificar a linha de comando Java registrada no `.out`.** Se um parâmetro esperado não está lá, o problema é em como o processo foi iniciado, não na JVM em si.
4. **Validar coerência entre `config.xml`, `nodemanager.properties` e `startup.properties`** antes de suspeitar de bugs do produto.
5. **Quando o erro for "Connection refused" para um componente interno**, verifique não só se o serviço está ativo, mas também **de onde** o cliente está tentando conectar (endereço, porta, protocolo).
