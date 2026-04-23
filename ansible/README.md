# Ansible — Configuração da VM e do WebLogic

Esta pasta contém o playbook e roles que entram via SSH na VM provisionada pelo Terraform e configuram toda a stack.

## Estrutura

```
ansible/
├── playbook.yml               # orquestra as roles em ordem
├── inventory                  # gerado pelo Make (git-ignored)
├── group_vars/
│   └── all.yml                # variáveis globais (versões, paths, senhas)
└── roles/
    ├── java/                  # instala JDK 11
    ├── weblogic/              # instala WebLogic 14c via silent install
    ├── domain/                # roda scripts WLST pra criar domínio
    └── deploy/                # builda e deploya a app JEE
```

## Fluxo

1. **`java`** — baixa e instala JDK 11, configura `JAVA_HOME`
2. **`weblogic`** — copia o instalador da máquina local, roda silent install, cria dir structure em `/u01/app/oracle/`
3. **`domain`** — executa scripts WLST em ordem (`01-create-domain.py` até `05-create-datasource.py`), inicia Node Manager e AdminServer
4. **`deploy`** — builda `hello.war` a partir de `../app/`, faz deploy via WLST

## Por que roles separadas

Permite execução parcial via `--tags`. Exemplos:

```bash
# Só redeploya a app
ansible-playbook -i inventory playbook.yml --tags deploy

# Só recria o domínio
ansible-playbook -i inventory playbook.yml --tags domain

# Não reinstala WebLogic (já instalado)
ansible-playbook -i inventory playbook.yml --skip-tags weblogic
```

## Idempotência

Todas as tasks usam módulos Ansible nativos (`apt`, `copy`, `template`, `systemd`) em vez de `shell`/`command` sempre que possível. As tasks que precisam rodar WLST são guardadas com `creates:` ou `changed_when:` pra evitar re-execução desnecessária.

## A implementar

- [ ] Role java
- [ ] Role weblogic (com silent response file)
- [ ] Role domain (systemd units pra Node Manager e AdminServer)
- [ ] Role deploy
- [ ] group_vars/all.yml com defaults
- [ ] handlers pra restart do Node Manager
