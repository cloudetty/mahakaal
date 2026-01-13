variable "tenancy_ocid" {}
variable "user_ocid" {}
variable "fingerprint" {}
variable "private_key_path" {}
variable "region" { default = "us-ashburn-1" }
variable "compartment_id" {}
variable "availability_domain" { description = "Find this in your OCI console (e.g. UocM:US-ASHBURN-AD-1)" }
variable "image_id" { description = "OCID for Ubuntu 24.04 Minimal aarch64 image in your region" }
variable "ssh_public_key" {}
