provider "openstack" {
  auth_url    = var.auth_url
  tenant_name = var.project_name
  user_name   = var.os_username
  password    = var.os_password
  domain_name = "Default"
  region      = var.region
}
