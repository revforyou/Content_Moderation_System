variable "suffix" {
  description = "Suffix for resource names (use net ID)"
  type        = string
  nullable    = false
}

variable "key" {
  description = "Name of key pair"
  type        = string
  default     = "id_rsa_chameleon_project26"
}

variable "nodes" {
  type = map(string)
  default = {
    "node-data"    = "192.168.1.11"
    "node-monitor" = "192.168.1.12"
    "node-train"   = "192.168.1.13"
    "node-infer"   = "192.168.1.14"
  }
}
