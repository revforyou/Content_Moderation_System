output "floating_ip_out" {
  description = "Floating IP assigned to node1"
  value       = openstack_networking_floatingip_v2.floating_ip.address
}

output "instance_ips" {
  description = "Fixed IPs of all nodes"
  value = {
    for name, inst in openstack_compute_instance_v2.nodes :
    name => inst.network[0].fixed_ip_v4
  }
}
