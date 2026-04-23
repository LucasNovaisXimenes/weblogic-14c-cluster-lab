# WLST Scripts — Configuração do domínio WebLogic

Scripts Python (WLST) que configuram o domínio após a instalação do binário WebLogic. Os scripts são **idempotentes** (podem rodar múltiplas vezes sem quebrar) e são executados em ordem pelo Ansible na role `domain`.

## Ordem de execução

| Ordem | Script | O que faz | Modo |
|---|---|---|---|
| 01 | `01-create-domain.py` | Cria `base_domain` com AdminServer | **offline** |
| 02 | `02-create-machine.py` | Cria Machine `LocalMachine` apontando pro NM | online |
| 03 | `03-create-managed-servers.py` | Cria `ms1` e `ms2`, associa à Machine | online |
| 04 | `04-create-cluster.py` | Cria `cluster1`, adiciona os MS | online |
| 05 | `05-create-datasource.py` | Cria DS `LabDS` targetado no cluster | online |
| 06 | `06-deploy-app.py` | Deploy do WAR da app no cluster | online |
| 99 | `99-destroy-domain.py` | Para servers, remove arquivos do domínio | offline |

**Offline** = edita o `config.xml` diretamente (AdminServer não precisa estar rodando).
**Online** = conecta no AdminServer via T3 e aplica mudanças em tempo real.

## Padrão de cada script

```python
# Cabeçalho: imports, args, logging
# 1. Conecta no cenário apropriado (offline/online)
# 2. Verifica se o recurso já existe (idempotência)
# 3. Se não existir, cria com startEdit/save/activate
# 4. Valida estado final
# 5. Desconecta
```

## Variáveis esperadas

Os scripts recebem credenciais e caminhos via variáveis de ambiente, setadas pelo Ansible:

- `WL_ADMIN_USER` — default `weblogic`
- `WL_ADMIN_PASSWORD` — senha inicial
- `WL_ADMIN_URL` — `t3://localhost:7001`
- `WL_DOMAIN_PATH` — `/u01/app/oracle/domains/base_domain`
- `WL_MIDDLEWARE_HOME` — `/u01/app/oracle/middleware`

## Como rodar individualmente (debug)

```bash
export WL_ADMIN_USER=weblogic
export WL_ADMIN_PASSWORD='welcome1Welcome1'
export WL_ADMIN_URL='t3://localhost:7001'

cd /u01/app/oracle/middleware/oracle_common/common/bin
./wlst.sh /path/to/03-create-managed-servers.py
```

## Decisões importantes

**Por que scripts separados em vez de um `setup.py` monolítico?**
Modularidade: cada script representa uma operação logicamente isolada, pode ser re-executado independentemente, e fica mais fácil de debugar. Em produção, times diferentes podem responsabilizar-se por pedaços diferentes (infra cria domínio, DBA cria DS, dev team deploya app).

**Por que Python e não shell + WLST?**
WLST **é** Python (Jython). Escrever direto em `.py` dá tooling normal (syntax highlighting, linter, IDE) e permite estruturar funções/módulos. Scripts `.sh` que fazem `echo` pra dentro de WLST viram um inferno de escaping.

## A implementar

- [ ] 01-create-domain.py (offline WLST usando template wls.jar)
- [ ] 02-create-machine.py
- [ ] 03-create-managed-servers.py
- [ ] 04-create-cluster.py
- [ ] 05-create-datasource.py (Derby por default, parametrizável)
- [ ] 06-deploy-app.py
- [ ] 99-destroy-domain.py
- [ ] common.py (funções utilitárias compartilhadas — connect, log, is_present)
