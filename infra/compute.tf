resource "oci_core_instance" "mahakaal_vm" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4
    memory_in_gbs = 24
  }

  display_name = "mahakaal-vm"

  source_details {
    source_type = "image"
    source_id   = var.image_id
  }

  create_vnic_details {
    subnet_id = oci_core_subnet.mahakaal_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(<<-EOF
                          #!/bin/bash
                          apt-get update
                          apt-get install -y docker.io docker-compose
                          systemctl start docker
                          systemctl enable docker
                          usermod -aG docker ubuntu
                          # Open firewall ports in Ubuntu 24.04
                          iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
                          iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
                          netfilter-persistent save
                          EOF
                          )
  }
}

output "public_ip" {
  value = oci_core_instance.mahakaal_vm.public_ip
}
