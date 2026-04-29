output "ecr_repository_url" {
  description = "ECR repository URL — push your Docker image here"
  value       = aws_ecr_repository.agora.repository_url
}

output "rds_endpoint" {
  description = "RDS MySQL endpoint — used in DATABASE_URL"
  value       = aws_db_instance.mysql.address
}

output "app_public_ip" {
  description = "EC2 public IP — the live application address"
  value       = aws_instance.app.public_ip
}

output "app_url" {
  description = "Direct URL to the running application"
  value       = "http://${aws_instance.app.public_dns}"
}

output "vpc_id" {
  value = aws_vpc.main.id
}
