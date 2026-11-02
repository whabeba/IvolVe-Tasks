#!/bin/bash
# Everything the Role does NOT allow must be rejected for the same ServiceAccount.
set -u
K="kubectl --kubeconfig=/tmp/sa.kubeconfig"

echo "--- create Deployment in the default namespace (different namespace) ---"
$K -n default create deployment nope --image=busybox:1.36 2>&1 | tail -1

echo "--- create a Pod in ivolve (different resource) ---"
$K -n ivolve run nope-pod --image=busybox:1.36 2>&1 | tail -1

echo "--- read the Deployment back (verb not granted) ---"
$K -n ivolve get deployments 2>&1 | tail -1

echo "--- delete the Deployment (verb not granted) ---"
$K -n ivolve delete deployment rbac-created 2>&1 | tail -1
