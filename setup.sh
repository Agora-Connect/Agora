#!/bin/bash
set -e

echo "Fetching secrets from AWS Secrets Manager"
export DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id agora/db-password \
  --region us-west-1 \
  --query SecretString \
  --output text)

echo "Step 1: Terraform Apply"
cd ~/Agora/terraform
terraform apply -auto-approve

echo "Step 2: Connect kubectl to EKS"
aws eks update-kubeconfig --region us-west-1 --name agora-cluster

echo "Step 3: Create Kubernetes Secret"
kubectl create secret generic agora-secrets \
  --from-literal=DATABASE_URL="mysql+pymysql://agora_admin:${DB_PASSWORD}@agora-db.cd6emqscs62y.us-west-1.rds.amazonaws.com:3306/agora" \
  --from-literal=SECRET_KEY="agora-production-secret-change-this" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Step 4: Deploy App with Helm"
helm upgrade --install agora ~/Agora/helm/agora

echo "Step 5: Install ArgoCD"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "Step 6: Create ArgoCD Application"
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: agora
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/Agora-Connect/Agora.git
    targetRevision: HEAD
    path: helm/agora
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

echo "Step 7: Install Prometheus + Grafana"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

echo "Done!"
kubectl get svc agora

