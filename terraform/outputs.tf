output "vm_ip" {
  description = "IP da VM no Hyper-V"
  value       = hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]
}

output "admin_url" {
  description = "URL do WebLogic Admin Console"
  value       = "http://${hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]}:7001/console"
}

output "app_url" {
  description = "URL da aplicação de demo no cluster"
  value       = "http://${hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]}:8001/hello/"
}

output "ms1_url" {
  description = "URL direta do Managed Server ms1"
  value       = "http://${hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]}:8001/hello/"
}

output "ms2_url" {
  description = "URL direta do Managed Server ms2"
  value       = "http://${hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]}:8002/hello/"
}

output "ssh_command" {
  description = "Comando SSH para acessar a VM"
  value       = "ssh ubuntu@${hyperv_machine_instance.wl_vm.network_adaptors[0].ip_addresses[0]}"
}
