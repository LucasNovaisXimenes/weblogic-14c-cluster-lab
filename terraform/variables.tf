variable "vm_name" {
  description = "Nome da VM no Hyper-V"
  type        = string
  default     = "weblogic-lab"
}

variable "vm_cpu" {
  description = "Número de vCPUs da VM"
  type        = number
  default     = 4
}

variable "vm_memory_mb" {
  description = "RAM da VM em MB"
  type        = number
  default     = 8192
}

variable "vm_disk_gb" {
  description = "Tamanho do disco em GB"
  type        = number
  default     = 40
}

variable "base_vhdx_path" {
  description = "Caminho absoluto do VHDX base (Ubuntu 24.04 cloud image) em binaries/"
  type        = string
}

variable "vm_switch_name" {
  description = "Nome do switch virtual Hyper-V"
  type        = string
  default     = "Default Switch"
}

variable "ssh_public_key" {
  description = "Chave SSH pública para injetar na VM via cloud-init"
  type        = string
}

variable "vm_generation" {
  description = "Geração da VM Hyper-V (1 ou 2)"
  type        = number
  default     = 2
}

variable "vhd_dir" {
  description = "Diretório onde o VHDX da VM será criado"
  type        = string
  default     = "C:\\Hyper-V\\VHDs"
}

variable "admin_password" {
  description = "Senha inicial do WebLogic AdminServer (mínimo 8 chars, 1 maiúscula, 1 número)"
  type        = string
  sensitive   = true
}
