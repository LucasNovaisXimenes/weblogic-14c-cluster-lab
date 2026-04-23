.DEFAULT_GOAL := help
SHELL := /bin/bash

# Cores pro output (porque faz bonito)
CYAN   := \033[0;36m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

TF_DIR      := terraform
ANSIBLE_DIR := ansible
VM_IP       = $(shell cd $(TF_DIR) && terraform output -raw vm_ip 2>/dev/null)

.PHONY: help up down vm-only configure deploy-app health ssh console logs \
        tf-init tf-plan tf-apply tf-destroy ansible-run clean

help: ## Mostra essa ajuda
	@echo -e "$(CYAN)WebLogic 14c Cluster Lab$(NC)"
	@echo ""
	@echo "Uso: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# ============================================================
# Pipelines principais
# ============================================================

up: tf-init tf-apply ansible-run health ## Sobe tudo: VM + WebLogic + app
	@echo -e "$(GREEN)✓ Lab pronto!$(NC)"
	@cd $(TF_DIR) && terraform output

down: tf-destroy ## Destrói a VM e limpa o estado
	@echo -e "$(YELLOW)✓ Lab destruído$(NC)"

# ============================================================
# Pipelines parciais (pra debug)
# ============================================================

vm-only: tf-init tf-apply ## Só provisiona a VM

configure: ansible-run ## Só roda o Ansible numa VM existente

deploy-app: ## Só refaz o deploy da app
	ansible-playbook -i $(ANSIBLE_DIR)/inventory $(ANSIBLE_DIR)/playbook.yml \
		--tags deploy

# ============================================================
# Terraform
# ============================================================

tf-init: ## terraform init
	@echo -e "$(CYAN)→ terraform init$(NC)"
	@cd $(TF_DIR) && terraform init -upgrade

tf-plan: ## terraform plan
	@cd $(TF_DIR) && terraform plan

tf-apply: ## terraform apply
	@echo -e "$(CYAN)→ terraform apply$(NC)"
	@cd $(TF_DIR) && terraform apply -auto-approve

tf-destroy: ## terraform destroy
	@echo -e "$(RED)→ terraform destroy$(NC)"
	@cd $(TF_DIR) && terraform destroy -auto-approve

# ============================================================
# Ansible
# ============================================================

ansible-run: _write_inventory ## Roda o playbook principal
	@echo -e "$(CYAN)→ ansible-playbook$(NC)"
	ansible-playbook -i $(ANSIBLE_DIR)/inventory $(ANSIBLE_DIR)/playbook.yml

_write_inventory:
	@echo -e "$(CYAN)→ gerando inventory$(NC)"
	@echo "[weblogic]" > $(ANSIBLE_DIR)/inventory
	@echo "$(VM_IP) ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa" \
		>> $(ANSIBLE_DIR)/inventory

# ============================================================
# Utilitários
# ============================================================

health: ## Health-check do ambiente
	@bash scripts/health-check.sh $(VM_IP)

ssh: ## SSH na VM
	@ssh ubuntu@$(VM_IP)

console: ## Abre o Admin Console
	@echo -e "$(CYAN)→ http://$(VM_IP):7001/console$(NC)"
	@python3 -c "import webbrowser; webbrowser.open('http://$(VM_IP):7001/console')" \
		|| xdg-open "http://$(VM_IP):7001/console" \
		|| start "http://$(VM_IP):7001/console"

logs: ## Tail dos logs dos MS
	@ssh ubuntu@$(VM_IP) \
		"tail -f /u01/app/oracle/domains/base_domain/servers/*/logs/*.out"

clean: ## Limpa arquivos temporários
	@rm -f $(ANSIBLE_DIR)/inventory
	@rm -rf $(TF_DIR)/.terraform $(TF_DIR)/.terraform.lock.hcl
	@rm -f $(TF_DIR)/terraform.tfstate*
	@echo -e "$(GREEN)✓ limpo$(NC)"
