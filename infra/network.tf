resource "oci_core_vcn" "mahakaal_vcn" {
  cidr_block     = "10.0.0.0/16"
  compartment_id = var.compartment_id
  display_name   = "mahakaal_vcn"
}

resource "oci_core_internet_gateway" "mahakaal_ig" {
  compartment_id = var.compartment_id
  display_name   = "mahakaal_ig"
  vcn_id         = oci_core_vcn.mahakaal_vcn.id
}

resource "oci_core_route_table" "mahakaal_rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.mahakaal_vcn.id
  display_name   = "mahakaal_rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.mahakaal_ig.id
  }
}

resource "oci_core_security_list" "mahakaal_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.mahakaal_vcn.id
  display_name   = "mahakaal_sl"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "mahakaal_subnet" {
  cidr_block        = "10.0.1.0/24"
  display_name      = "mahakaal_subnet"
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.mahakaal_vcn.id
  route_table_id    = oci_core_route_table.mahakaal_rt.id
  security_list_ids = [oci_core_security_list.mahakaal_sl.id]
}
