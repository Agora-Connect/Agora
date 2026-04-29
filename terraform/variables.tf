variable "aws_region" {
  default = "us-west-1"
}

variable "project" {
  default = "agora"
}

variable "db_username" {
  default = "agora_admin"
}

variable "db_password" {
  description = "RDS MySQL password — set via TF_VAR_db_password or terraform.tfvars"
  sensitive   = true
}

variable "app_secret_key" {
  description = "Flask SECRET_KEY — set via TF_VAR_app_secret_key or terraform.tfvars"
  sensitive   = true
}
