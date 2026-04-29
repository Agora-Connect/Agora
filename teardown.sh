#!/bin/bash
# teardown.sh — destroys all Agora AWS infrastructure
# Usage: ./teardown.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓ $1${NC}"; }
step() { echo -e "\n${YELLOW}▶ $1${NC}"; }
fail() { echo -e "\n${RED}✗ ERROR: $1${NC}\n"; exit 1; }

echo -e "${RED}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║   Agora — Teardown (destroys all AWS infra)  ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  This will permanently destroy:"
echo "    • EC2 instance"
echo "    • RDS MySQL database (all data lost)"
echo "    • ECR repository (all images deleted)"
echo "    • VPC, subnets, security groups"
echo ""
read -r -p "  Are you sure? Type 'yes' to continue: " CONFIRM
[ "$CONFIRM" = "yes" ] || { echo "  Aborted."; exit 0; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"

command -v terraform >/dev/null 2>&1 || fail "terraform not installed"
command -v aws       >/dev/null 2>&1 || fail "aws cli not installed"
aws sts get-caller-identity >/dev/null 2>&1 || fail "AWS credentials not configured — run 'aws configure'"

step "Destroying AWS infrastructure..."
cd "$TERRAFORM_DIR"
terraform init -input=false -no-color >/dev/null
terraform destroy -auto-approve -input=false
ok "All infrastructure destroyed"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗"
echo    "║          Agora teardown complete.            ║"
echo -e "╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  To redeploy:  ./setup.sh"
echo ""
