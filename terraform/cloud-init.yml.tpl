#cloud-config
# Template renderizado pelo Terraform — não editar diretamente.

hostname: weblogic-lab
fqdn: weblogic-lab.local

users:
  - name: ubuntu
    groups: [sudo]
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    lock_passwd: true
    ssh_authorized_keys:
      - ${ssh_public_key}

package_update: true
package_upgrade: false

packages:
  - curl
  - wget
  - unzip
  - net-tools
  - htop
  - python3
  - python3-pip

# Cria estrutura de diretórios Oracle
runcmd:
  - mkdir -p /u01/app/oracle/middleware
  - mkdir -p /u01/app/oracle/domains
  - mkdir -p /u01/stage
  - chown -R ubuntu:ubuntu /u01
  - timedatectl set-timezone America/Sao_Paulo

write_files:
  - path: /etc/sysctl.d/99-weblogic.conf
    content: |
      # Aumenta file descriptors e conexões para WebLogic
      fs.file-max = 65536
      net.core.somaxconn = 1024
    permissions: '0644'

final_message: "Cloud-init concluído. VM pronta para o Ansible."
