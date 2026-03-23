variable "aws_region" {
    default  = "us-west-1"
}

variable "project"{
    default = "agora"
}

variable "db_username" {
    default = "agora_admin"
}

variable "db_password" {
    description = "RDS MySQL password"
    sensitive = true
}

