resource "aws_security_group" "app" {
    name = "${var.project}-app-sg"
    vpc_id = aws_vpc.main.id

    ingress { # in bound traffic 
        from_port = 8000
        to_port = 8000
        protocol = "tcp"
        cidr_blocks = ["10.0.0.0/16"]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "${var.project}-app-sg"
    }
}
resource "aws_security_group" "rds" {
    name = "${var.project}-rds-sg"
    vpc_id = aws_vpc.main.id

    ingress {
        from_port = 3306 # MySQL port
        to_port = 3306
        protocol = "tcp"
        security_groups = [aws_security_group.app.id]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"] # allow outgoing traffic to everywhere
    }
    tags = {
        Name = "${var.project}-rds-sg"
    }
}


