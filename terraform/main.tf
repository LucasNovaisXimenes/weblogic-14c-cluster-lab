locals {
  vm_vhd_path  = "${var.vhd_dir}\\${var.vm_name}.vhdx"
  cloud_init   = templatefile("${path.module}/cloud-init.yml.tpl", {
    ssh_public_key = var.ssh_public_key
  })
}

# Disco principal: clone do VHDX base Ubuntu 24.04
resource "hyperv_vhd" "vm_disk" {
  path   = local.vm_vhd_path
  source = var.base_vhdx_path
  size   = var.vm_disk_gb * 1024 * 1024 * 1024
}

# Disco de cloud-init (NoCloud ISO via VHD auxiliar)
resource "hyperv_vhd" "cloud_init_disk" {
  path = "${var.vhd_dir}\\${var.vm_name}-cloud-init.vhdx"
  size = 10 * 1024 * 1024  # 10 MB
}

resource "hyperv_machine_instance" "wl_vm" {
  name       = var.vm_name
  generation = var.vm_generation
  state      = "Running"

  processor_count = var.vm_cpu

  dynamic_memory_enabled            = false
  static_memory_maximum_bytes       = var.vm_memory_mb * 1024 * 1024
  static_memory_startup_bytes       = var.vm_memory_mb * 1024 * 1024
  static_memory_minimum_bytes       = var.vm_memory_mb * 1024 * 1024

  # Boot: disco principal, depois rede
  vm_firmware {
    enable_secure_boot    = false
    boot_order {
      boot_type           = "HardDiskDrive"
      controller_number   = "0"
      controller_location = "0"
    }
  }

  network_adaptors {
    name        = "Network Adapter"
    switch_name = var.vm_switch_name
  }

  hard_disk_drives {
    controller_type     = "Scsi"
    controller_number   = "0"
    controller_location = "0"
    path                = hyperv_vhd.vm_disk.path
  }

  hard_disk_drives {
    controller_type     = "Scsi"
    controller_number   = "0"
    controller_location = "1"
    path                = hyperv_vhd.cloud_init_disk.path
  }

  # Aguarda a VM responder na porta SSH antes de liberar o apply
  provisioner "local-exec" {
    command = <<-EOT
      echo "Aguardando VM iniciar (SSH :22)..."
      for i in $(seq 1 60); do
        if nc -z -w2 ${self.network_adaptors[0].ip_addresses[0]} 22 2>/dev/null; then
          echo "SSH disponivel!"
          exit 0
        fi
        echo "Tentativa $i/60..."
        sleep 5
      done
      echo "Timeout aguardando SSH"
      exit 1
    EOT
    interpreter = ["bash", "-c"]
  }

  depends_on = [hyperv_vhd.vm_disk, hyperv_vhd.cloud_init_disk]
}
