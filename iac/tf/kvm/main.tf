resource "openstack_objectstorage_container_v1" "persist_container" {
  name = "object-persist-project26"
  metadata = {
    project     = "content-moderation"
    environment = "production"
    purpose     = "training-and-retraining"
  }
}

resource "openstack_blockstorage_volume_v3" "mlops_volume" {
  name        = "block-persist-project26"
  size        = 5 
  volume_type = "default"
  metadata = {
    purpose = "ml-artifacts"
    env     = "project26"
  }
}

resource "openstack_compute_volume_attach_v2" "attach_volume_to_node1" {
  instance_id = openstack_compute_instance_v2.nodes["node1"].id
  volume_id   = openstack_blockstorage_volume_v3.mlops_volume.id
}


resource "openstack_networking_network_v2" "private_net" {
  name                  = "private-net-mlops-${var.suffix}"
  port_security_enabled = false
}

resource "openstack_networking_subnet_v2" "private_subnet" {
  name       = "private-subnet-mlops-${var.suffix}"
  network_id = openstack_networking_network_v2.private_net.id
  cidr       = "192.168.1.0/24"
  no_gateway = true
}

resource "openstack_networking_port_v2" "private_net_ports" {
  for_each              = var.nodes
  name                  = "port-${each.key}-mlops-${var.suffix}"
  network_id            = openstack_networking_network_v2.private_net.id
  port_security_enabled = false

  fixed_ip {
    subnet_id  = openstack_networking_subnet_v2.private_subnet.id
    ip_address = each.value
  }
}

resource "openstack_networking_port_v2" "sharednet2_ports" {
  for_each   = var.nodes
  name       = "sharednet2-${each.key}-mlops-${var.suffix}"
  network_id = data.openstack_networking_network_v2.sharednet2.id
  security_group_ids = [
    data.openstack_networking_secgroup_v2.allow_ssh.id,
    data.openstack_networking_secgroup_v2.allow_9001.id,
    data.openstack_networking_secgroup_v2.allow_8000.id,
    data.openstack_networking_secgroup_v2.allow_8080.id,
    data.openstack_networking_secgroup_v2.allow_8081.id,
    data.openstack_networking_secgroup_v2.allow_http_80.id,
    data.openstack_networking_secgroup_v2.allow_9090.id,
    data.openstack_networking_secgroup_v2.allow_8888.id,
    data.openstack_networking_secgroup_v2.allow_9000.id
  ]
}

resource "openstack_compute_instance_v2" "nodes" {
  for_each = var.nodes

  name        = "${each.key}-mlops-${var.suffix}"
  image_name  = "CC-Ubuntu24.04"
  flavor_name = "m1.medium"
  key_pair    = var.key

  network {
    port = openstack_networking_port_v2.sharednet2_ports[each.key].id
  }

  network {
    port = openstack_networking_port_v2.private_net_ports[each.key].id
  }

  user_data = <<-EOF
    #! /bin/bash
    sudo echo "127.0.1.1 ${each.key}-mlops-${var.suffix}" >> /etc/hosts
    su cc -c /usr/local/bin/cc-load-public-keys
  EOF
}

resource "openstack_networking_floatingip_v2" "floating_ip" {
  pool        = "public"
  description = "MLOps IP for ${var.suffix}"
  port_id = openstack_networking_port_v2.sharednet2_ports["node-monitor"].id
}

