# Arquitetura do WebLogic 14c Cluster Lab

## Visão geral

O lab provisiona, de forma totalmente automatizada, um ambiente WebLogic 14.1.1 completo rodando dentro de uma VM Ubuntu 24.04 no Hyper-V do host Windows. O ciclo completo — de zero até aplicação respondendo — é disparado por um único `make up`.

## Componentes e responsabilidades

### Host Windows

| Componente | Ferramenta | Papel |
|---|---|---|
| Provisionamento de VM | Terraform + provider `taliesins/hyperv` | Cria e configura a VM via WinRM com o Hyper-V local |
| Configuração do SO | Ansible (via SSH) | Instala JDK, WebLogic e configura o sistema |
| Orquestração | GNU Make | Coordena terraform → ansible → health-check |

### VM Ubuntu 24.04

```
/u01/app/oracle/
├── middleware/          ← WebLogic 14.1.1 (ORACLE_HOME)
│   ├── wlserver/
│   │   ├── server/bin/ ← startWebLogic.sh, startNodeManager.sh
│   │   └── common/
│   │       ├── derby/  ← Derby embutido (banco de demo)
│   │       └── bin/    ← wlst.sh
│   └── oracle_common/
│       └── common/bin/ ← wlst.sh (link canônico)
└── domains/
    └── base_domain/    ← DOMAIN_HOME
        ├── config/
        │   └── config.xml
        ├── nodemanager/
        │   └── nodemanager.log
        └── servers/
            ├── AdminServer/logs/
            ├── ms1/logs/
            └── ms2/logs/
```

## Topologia WebLogic

```
AdminServer (:7001)
     │
     └── gerencia via T3
           │
     NodeManager (:5556, Plain)
           │
     ┌─────┴─────┐
   ms1(:8001)  ms2(:8002)
     └─────┬─────┘
       cluster1
           │
        LabDS (pool JDBC → Derby :1527 → labdb)
```

### Por que Plain NM (não SSL)?

No lab, toda comunicação é localhost. SSL adicionaria gestão de keystores sem benefício real. Em produção, use `Ssl` com mutual TLS entre AdminServer e Node Manager.

## Fluxo de rede

| Origem | Destino | Porta | Protocolo | Finalidade |
|---|---|---|---|---|
| Host Windows | VM | 22 | SSH | Ansible + acesso manual |
| Host Windows | VM | 7001 | HTTP/T3 | Admin Console, `make console` |
| Host Windows | VM | 8001-8002 | HTTP | Acesso à aplicação, `make health` |
| AdminServer | NodeManager | 5556 | T3 (Plain) | Iniciar/parar Managed Servers |
| Managed Servers | AdminServer | 7001 | T3 | Registro, heartbeat |
| Managed Servers | Derby | 1527 | DRDA | JDBC via pool LabDS |

## Ciclo de vida de um deploy

1. `make up` dispara `terraform apply` → VM criada com cloud-init
2. Terraform aguarda SSH disponível (provisioner `local-exec`)
3. Makefile escreve `ansible/inventory` com o IP da VM
4. `ansible-playbook` roda 4 roles em sequência:
   - **java**: instala OpenJDK 11
   - **weblogic**: silent install via response file
   - **domain**: executa WLST 01→05, inicia NM e AdminServer como serviços systemd, inicia Managed Servers
   - **deploy**: empacota `app/` como WAR, deploy via WLST 06
5. `make health` valida todos os endpoints

## Serviços systemd

Ambos os processos WebLogic são gerenciados pelo systemd, garantindo:
- Auto-restart em falha (com delay para evitar restart storm)
- Logs centralizados via `StandardOutput`
- Inicialização automática em reboot da VM

| Serviço | Unidade |
|---|---|
| Node Manager | `weblogic-nodemanager.service` |
| AdminServer | `weblogic-adminserver.service` |

Os Managed Servers **não** têm unidade systemd — são controlados pelo Node Manager, que é o modelo operacional correto do WebLogic. O NM recebe o sinal de start do AdminServer e é responsável por fazer o restart automático em caso de falha (via `AutoRestart` e `RestartDelaySeconds`).

## Idempotência

Cada script WLST verifica a existência do recurso antes de criá-lo. Reexecutar o playbook é seguro e não duplica objetos no domínio. A exceção é `06-deploy-app.py`, que faz undeploy + redeploy para garantir que a versão mais recente do WAR seja aplicada.

## Limites conhecidos do lab

- **Single-host**: NM, AdminServer e os dois MS rodam na mesma VM. Em produção, cada host teria seu próprio NM.
- **Derby como banco**: adequado para demo. Não é HA, não suporta carga real.
- **Sem proxy/load balancer**: em produção, o cluster seria exposto via Oracle HTTP Server ou Apache com mod_wl_ohs, não diretamente.
- **Sem SSL/TLS**: Admin Console e aplicação trafegam em HTTP claro.
