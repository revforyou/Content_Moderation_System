resource "openstack_compute_instance_v2" "node_data" {
  name            = "node-data"
  image_name      = var.image_name
  flavor_name     = var.flavor_name
  key_pair        = var.key_pair
  security_groups = ["default"]
}
