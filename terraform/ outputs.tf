output "ecr_repository_url" {
    value = aws_ecr_repository.agora.repository_url

}

output "rds_endpoint" {
    value = aws_db_instance.mysql.endpoint

}

output "vpc_id" {
    value = aws_vpc.main.id   # needed when creating EKS in the next phase
}

output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}