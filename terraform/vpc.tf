# VPC
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true
    tags = {
        Name = "${var.project}-vpc"
    }
}

# public subnets (load balancer + NAT Gateway)

resource "aws_subnet" "public_a" {
    vpc_id = aws_vpc.main.id # put this subnet inside this vpc
    cidr_block = "10.0.1.0/24" # 256 ip ranges carved from the vpc range
                            # public_a gets 10.0.1.0 - 10.0.1.255
    availability_zone = "${var.aws_region}a"
    map_public_ip_on_launch = true # any resource launches in this
                                    # public subnet gets public IP automatically
    tags = {
        Name = "${var.project}-public-a"
    }
}
resource "aws_subnet" "public_b" {
    vpc_id = aws_vpc.main.id # put this subnet inside this vpc
    cidr_block = "10.0.2.0/24"  
    availability_zone = "${var.aws_region}b"
    map_public_ip_on_launch = true # any resource launches in this
                                    # public subnet gets public IP automatically
    tags = {
        Name = "${var.project}-public-b"
    }
}

# private subnet
resource "aws_subnet" "private_a" {
    vpc_id = aws_vpc.main.id # put this subnet inside this vpc
    cidr_block = "10.0.3.0/24"
    availability_zone = "${var.aws_region}a"
    tags = {
        Name = "${var.project}-private-a"
    }
}
resource "aws_subnet" "private_b" {
    vpc_id = aws_vpc.main.id # put this subnet inside this vpc
    cidr_block = "10.0.4.0/24"  
    availability_zone = "${var.aws_region}b"
    tags = {
        Name = "${var.project}-private-b"
    }
}

# Private Subnet DB
resource "aws_subnet" "db_a" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.5.0/24" # 10.0.5.x — database servers only
    availability_zone = "${var.aws_region}a"
    tags = { Name = "${var.project}-db-a" }
}

resource "aws_subnet" "db_b" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.6.0/24"
    availability_zone = "${var.aws_region}b"
    tags = { Name = "${var.project}-db-b" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
    vpc_id = aws_vpc.main.id # attach to our VPC
    tags = {
        Name = "${var.project}-igw"
    }
}

# NAT Gateway
resource "aws_eip" "nat" {
    domain = "vpc"
    tags = {
        Name = "${var.project}-nat-eip"
    }
}

resource "aws_nat_gateway" "main" {
    allocation_id = aws_eip.nat.id # use the Elastic IP we just created
    subnet_id = aws_subnet.public_a.id # lives in public subnet 
    tags = { Name = "${var.project}-nat" }
    depends_on = [aws_internet_gateway.main] # don't create NAT until IGW exists
                                            # because NAT needs IGW to function
}

# Route Table
resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id 
    route {
        cidr_block = "0.0.0.0/0" # routing all traffic
        gateway_id = aws_internet_gateway.main.id # send it to internet gateway
    }
    tags = {
        Name = "${var.project}-public-rt"
    }
}

resource "aws_route_table_association" "public_a" {
    subnet_id = aws_subnet.public_a.id
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
    subnet_id = aws_subnet.public_b.id
    route_table_id = aws_route_table.public.id
}


resource "aws_route_table" "private" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.main.id # outbound traffic through NAT gateway
    }
    tags = {
        "Name" = "${var.project}-private-rt"
    }
}
# any outbound traffic from private subnet goes to/through nat gateway route tables

resource "aws_route_table_association" "private_a" {
    subnet_id = aws_subnet.private_a.id
    route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
    subnet_id = aws_subnet.private_b.id
    route_table_id = aws_route_table.private.id
}


