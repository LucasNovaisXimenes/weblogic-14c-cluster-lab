terraform {
  required_version = ">= 1.6"

  required_providers {
    hyperv = {
      source  = "taliesins/hyperv"
      version = "~> 1.0"
    }
  }
}

provider "hyperv" {
  # Usa WinRM para se comunicar com o Hyper-V local.
  # Por padrão conecta em localhost com autenticação Windows integrada.
  # Nenhuma variável extra necessária quando rodando no mesmo host.
}
