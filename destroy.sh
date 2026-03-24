#!/bin/bash
set -e

echo "=== Checking if EKS cluster exists ==="
if aws eks describe-cluster --name agora-cluster --region us-west-1 &>/dev/null; then
    echo "Cluster found — cleaning up Kubernetes resources first"

    aws eks update-kubeconfig --region us-west-1 --name agora-cluster

    echo "=== Step 1: Delete Kubernetes App Resources ==="
    helm uninstall agora --ignore-not-found
    helm uninstall monitoring -n monitoring --ignore-not-found

    echo "=== Step 2: Delete ArgoCD ==="
    kubectl delete application agora -n argocd --ignore-not-found
    kubectl delete namespace argocd --ignore-not-found

    echo "=== Step 3: Wait for Load Balancer to be deleted ==="
    echo "Waiting 60 seconds for AWS to remove the Load Balancer..."
    sleep 60
else
    echo "No EKS cluster found — skipping Kubernetes cleanup"
fi

echo "=== Step 4: Delete ECR Images ==="
IMAGE_IDS=$(aws ecr list-images --repository-name agora --region us-west-1 --query 'imageIds[*]' --output json 2>/dev/null)
if [ "$IMAGE_IDS" != "[]" ] && [ -n "$IMAGE_IDS" ]; then
    aws ecr batch-delete-image \
      --repository-name agora \
      --region us-west-1 \
      --image-ids "$IMAGE_IDS"
    echo "ECR images deleted"
else
    echo "No ECR images found — skipping"
fi

echo "=== Step 5: Terraform Destroy ==="
cd ~/Agora/terraform
terraform destroy -auto-approve

echo "=== Done! Everything destroyed ==="

