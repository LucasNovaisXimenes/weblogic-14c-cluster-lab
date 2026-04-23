# Terraform — Provisionamento da VM

Esta pasta contém os módulos Terraform que provisionam a VM Ubuntu 24.04 no Hyper-V local.

## Estrutura prevista

```
terraform/
├── main.tf              # provider hyperv + recursos principais
├── variables.tf         # entradas configuráveis (CPU, RAM, paths)
├── outputs.tf           # IP da VM, URLs finais
├── cloud-init.yml.tpl   # template cloud-init (user, SSH, pacotes base)
├── terraform.tfvars.example  # exemplo pro usuário copiar
└── versions.tf          # lock de versões do provider
```

## Provider usado

[`taliesins/hyperv`](https://registry.terraform.io/providers/taliesins/hyperv/latest) — community provider, único disponível pra Hyper-V.

**Nota de transparência:** o provider Hyper-V tem limitações conhecidas em criação de VM from scratch. Esta implementação parte de um VHDX base do Ubuntu 24.04 cloud image (fornecido pelo usuário em `binaries/`), que o Terraform clona e customiza via cloud-init.

## Variáveis principais

| Variável | Default | Descrição |
|---|---|---|
| `vm_name` | `weblogic-lab` | Nome da VM no Hyper-V |
| `vm_cpu` | `4` | vCPUs |
| `vm_memory_mb` | `8192` | RAM em MB |
| `vm_disk_gb` | `40` | Disco em GB |
| `base_vhdx_path` | — | Caminho do VHDX base (Ubuntu cloud image) |
| `vm_switch_name` | `Default Switch` | Switch virtual Hyper-V |
| `ssh_public_key` | — | Chave SSH pública pra injetar na VM |

## A implementar

- [ ] Provider e versions.tf
- [ ] Recurso `hyperv_vhd` (clone do base)
- [ ] Recurso `hyperv_machine_instance` (a VM)
- [ ] cloud-init com user `ubuntu` e SSH key
- [ ] Outputs com IP dinâmico da VM
