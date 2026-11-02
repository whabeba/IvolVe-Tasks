#!/bin/bash
# The two actions the Role allows: create and update Deployments in ivolve.
set -eu
cd "$(dirname "$0")"
./make-sa-kubeconfig.sh
K="kubectl --kubeconfig=/tmp/sa.kubeconfig"

# start from a clean object so the script can be re-run
kubectl delete deployment rbac-created -n ivolve --ignore-not-found >/dev/null

echo "--- create Deployment in ivolve (allowed) ---"
$K create -f 05-test-deployment.yaml
kubectl get deploy rbac-created -n ivolve

echo "--- update the same Deployment (allowed) ---"
TOKEN=$(kubectl get secret jenkinssa-token -n ivolve -o jsonpath='{.data.token}' | base64 -d)
SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
RV=$(kubectl get deploy rbac-created -n ivolve -o jsonpath='{.metadata.resourceVersion}')

cat > /tmp/put.json <<EOF
{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"rbac-created","namespace":"ivolve","resourceVersion":"${RV}","labels":{"app":"rbac-created","updated":"by-sa"}},"spec":{"replicas":2,"selector":{"matchLabels":{"app":"rbac-created"}},"template":{"metadata":{"labels":{"app":"rbac-created"}},"spec":{"containers":[{"name":"app","image":"busybox:1.36","imagePullPolicy":"IfNotPresent","command":["sh","-c","sleep 3600"]}]}}}}
EOF

curl -s -k -o /dev/null -w "PUT deployment (replicas 1 -> 2) -> HTTP %{http_code}\n" \
  -X PUT -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
  --data @/tmp/put.json \
  "${SERVER}/apis/apps/v1/namespaces/ivolve/deployments/rbac-created"

kubectl get deploy rbac-created -n ivolve -o jsonpath='replicas now: {.spec.replicas}{"\n"}'
