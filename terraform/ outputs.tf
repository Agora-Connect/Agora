output "ecr_repository_url" {
    value = aws_ecr_repository.agora.repository_url
    # after terraform apply, prints something like:
    # 123456789.dkr.ecr.us-west-1.amazonaws.com/agora
    # you need this URL to push Docker images
}

output "rds_endpoint" {
    value = aws_db_instance.mysql.endpoint
    # prints something like:
    # agora-db.abc123.us-west-1.rds.amazonaws.com:3306
    # this goes into your DATABASE_URL env var
}

output "vpc_id" {
    value = aws_vpc.main.id   # needed when creating EKS in the next phase
}