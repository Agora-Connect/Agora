#!/bin/bash
# setup.sh — brings the full Agora stack live on AWS
# Usage: ./setup.sh
#
# Prerequisites:
#   - terraform    (brew install terraform)
#   - aws cli      (brew install awscli) + configured via 'aws configure'
#   - podman       (brew install podman)
#   - terraform/terraform.tfvars exists (copy from terraform.tfvars.example and fill in values)

set -e

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓ $1${NC}"; }
step() { echo -e "\n${YELLOW}▶ $1${NC}"; }
fail() { echo -e "\n${RED}✗ ERROR: $1${NC}\n"; exit 1; }

echo -e "${GREEN}"
echo "  ╔═══════════════════════════════╗"
echo "  ║   Agora — Deployment Setup    ║"
echo "  ╚═══════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"
REGION="us-west-1"

# ── Step 0: Prerequisites check ───────────────────────────────────────────────
step "Checking prerequisites..."
command -v terraform >/dev/null 2>&1 || fail "terraform not installed — brew install terraform"
command -v aws       >/dev/null 2>&1 || fail "aws cli not installed — brew install awscli"
command -v podman    >/dev/null 2>&1 || fail "podman not installed — brew install podman"
[ -f "$TERRAFORM_DIR/terraform.tfvars" ] || \
  fail "terraform/terraform.tfvars not found\nCopy terraform/terraform.tfvars.example and fill in your values"
aws sts get-caller-identity >/dev/null 2>&1 || \
  fail "AWS credentials not configured — run 'aws configure'"
ok "All prerequisites met"

# ── Step 1: Terraform init + apply ────────────────────────────────────────────
step "Step 1/5 — Provisioning AWS infrastructure (VPC, RDS, ECR, EC2)..."
cd "$TERRAFORM_DIR"
terraform init -input=false -upgrade -no-color >/dev/null
terraform apply -auto-approve -input=false
ok "Infrastructure provisioned"

# Read outputs
ECR_URL=$(terraform output -raw ecr_repository_url)
APP_URL=$(terraform output -raw app_url)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=agora-app" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text --region "$REGION")
ok "ECR  → $ECR_URL"
ok "App  → $APP_URL"
ok "RDS  → $RDS_ENDPOINT"
ok "EC2  → $INSTANCE_ID"

# ── Step 2: Build image ───────────────────────────────────────────────────────
step "Step 2/5 — Building Docker image (linux/arm64)..."
cd "$SCRIPT_DIR"
podman build --platform linux/arm64 -t agora:latest .
ok "Image built"

# ── Step 3: Push to ECR ───────────────────────────────────────────────────────
step "Step 3/5 — Pushing image to ECR..."
aws ecr get-login-password --region "$REGION" \
  | podman login --username AWS --password-stdin "$ECR_URL"
podman tag agora:latest "$ECR_URL:latest"
podman push "$ECR_URL:latest"
ok "Image pushed"

# ── Step 4: Ensure container is running on EC2 ───────────────────────────────
step "Step 4/5 — Waiting for EC2 SSM agent..."
for i in $(seq 1 24); do
  STATUS=$(aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$INSTANCE_ID" \
    --region "$REGION" \
    --query 'InstanceInformationList[0].PingStatus' \
    --output text 2>/dev/null)
  [ "$STATUS" = "Online" ] && break
  echo "  Waiting for SSM (attempt $i/24)..."
  sleep 10
done
[ "$STATUS" = "Online" ] || fail "SSM agent did not come online — check EC2 IAM role has AmazonSSMManagedInstanceCore"
ok "EC2 online via SSM"

# Check if container started automatically from user-data
CHECK_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["docker ps --filter name=agora --format \"{{.Status}}\""]' \
  --region "$REGION" \
  --query 'Command.CommandId' \
  --output text)
sleep 8
CONTAINER_STATUS=$(aws ssm get-command-invocation \
  --command-id "$CHECK_ID" \
  --instance-id "$INSTANCE_ID" \
  --region "$REGION" \
  --query 'StandardOutputContent' \
  --output text 2>/dev/null)

if echo "$CONTAINER_STATUS" | grep -q "Up"; then
  ok "Container running (started by user-data)"
else
  echo "  Container not yet running — starting via SSM..."
  DB_USER=$(grep 'db_username' "$TERRAFORM_DIR/terraform.tfvars" | grep -o '"[^"]*"' | tail -1 | tr -d '"')
  DB_PASS=$(grep 'db_password' "$TERRAFORM_DIR/terraform.tfvars" | grep -o '"[^"]*"' | tail -1 | tr -d '"')
  SECRET_KEY=$(grep 'app_secret_key' "$TERRAFORM_DIR/terraform.tfvars" | grep -o '"[^"]*"' | tail -1 | tr -d '"')
  DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASS}@${RDS_ENDPOINT}:3306/agora_db"

  START_ID=$(aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[
      \"aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL\",
      \"docker pull $ECR_URL:latest\",
      \"docker stop agora 2>/dev/null || true\",
      \"docker rm   agora 2>/dev/null || true\",
      \"docker run -d --name agora --restart unless-stopped -p 80:8000 -e SECRET_KEY='$SECRET_KEY' -e DATABASE_URL='$DATABASE_URL' $ECR_URL:latest\"
    ]" \
    --region "$REGION" \
    --query 'Command.CommandId' \
    --output text)
  sleep 20
  RESULT=$(aws ssm get-command-invocation \
    --command-id "$START_ID" --instance-id "$INSTANCE_ID" \
    --region "$REGION" --query 'Status' --output text 2>/dev/null)
  [ "$RESULT" = "Success" ] || fail "Could not start container. Check AWS Console → EC2 → Systems Manager → Run Command"
  ok "Container started via SSM"
fi

# ── Step 5: Verify app responds ───────────────────────────────────────────────
step "Step 5/5 — Verifying app is live..."
HTTP_CODE="000"
for i in $(seq 1 18); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 8 "$APP_URL" 2>/dev/null || echo "000")
  ( [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] ) && break
  echo "  Waiting for app (attempt $i/18, HTTP $HTTP_CODE)..."
  sleep 10
done
( [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] ) || \
  fail "App not responding (HTTP $HTTP_CODE). Check logs:\n  aws ssm start-session --target $INSTANCE_ID --region $REGION"
ok "App responding HTTP $HTTP_CODE"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗"
echo    "║              Agora is live on AWS!                   ║"
echo -e "╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  URL : ${GREEN}$APP_URL${NC}"
echo -e "${GREEN}║${NC}  RDS : $RDS_ENDPOINT"
echo -e "${GREEN}║${NC}  EC2 : $INSTANCE_ID"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  To tear everything down:  ./teardown.sh"
echo ""
