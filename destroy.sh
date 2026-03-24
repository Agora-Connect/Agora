#!/bin/bash
set -e

echo "Step 1: Delete Kubernetes App Resources"
helm uninstall agora --ignore-not-found
helm uninstall monitoring -n monitoring --ignore-not-found

echo "Step 2: Delete ArgoCD Application"
kubectl delete application agora -n argocd --ignore-not-found

echo "Step 3: Delete ArgoCD"
kubectl delete namespace argocd --ignore-not-found

echo "Step 4: Wait for Load Balancer to be deleted"
echo "Waiting 30 seconds for AWS to remove the Load Balancer..."
sleep 30

echo "Step 5: Terraform Destroy"
cd ~/Agora/terraform
terraform destroy -auto-approve

echo "Done! Everything destroyed"

