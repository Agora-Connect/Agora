# IAM role that allows the EC2 instance to pull images from ECR
resource "aws_iam_role" "ec2" {
  name = "${var.project}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_ecr" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.ec2.name
}

# SSM allows connecting to the instance via AWS console/CLI without SSH keys
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# arm64 Amazon Linux 2023 AMI — matches the arm64 image built on Apple Silicon
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 instance — t4g.micro is arm64 and free-tier eligible
resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t4g.micro"
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  user_data = <<-EOF
    #!/bin/bash
    exec > /var/log/user-data.log 2>&1

    echo "=== Starting Agora deployment ==="

    # Install Docker
    dnf update -y
    dnf install -y docker
    systemctl enable docker
    systemctl start docker

    # Wait for Docker daemon to be ready
    timeout 30 sh -c 'until docker info >/dev/null 2>&1; do sleep 2; done'
    echo "Docker ready"

    # Authenticate to ECR
    aws ecr get-login-password --region ${var.aws_region} \
      | docker login --username AWS --password-stdin ${aws_ecr_repository.agora.repository_url}
    echo "ECR login OK"

    # Pull the image
    docker pull ${aws_ecr_repository.agora.repository_url}:latest
    echo "Image pulled"

    # Start the container
    docker run -d \
      --name agora \
      --restart unless-stopped \
      -p 80:8000 \
      -e SECRET_KEY="${var.app_secret_key}" \
      -e DATABASE_URL="mysql+pymysql://${var.db_username}:${var.db_password}@${aws_db_instance.mysql.address}:3306/agora_db" \
      ${aws_ecr_repository.agora.repository_url}:latest

    echo "=== Agora container started ==="
  EOF

  tags = {
    Name = "${var.project}-app"
  }

  # Ensure RDS and ECR exist before launching the instance
  depends_on = [
    aws_db_instance.mysql,
    aws_ecr_repository.agora,
  ]
}
