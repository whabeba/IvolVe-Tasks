#!/bin/bash
# Builds /tmp/sa.kubeconfig that authenticates ONLY as the jenkinssa ServiceAccount.
# Using the token alone (no admin client certificate) is what makes the test valid.
set -eu
TOKEN=$(kubectl get secret jenkinssa-token -n ivolve -o jsonpath='{.data.token}' | base64 -d)
SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

cat > /tmp/sa.kubeconfig <<EOF
apiVersion: v1
kind: Config
clusters:
  - name: sa
    cluster:
      server: ${SERVER}
      insecure-skip-tls-verify: true
users:
  - name: sa
    user:
      token: ${TOKEN}
contexts:
  - name: sa
    context:
      cluster: sa
      user: sa
      namespace: ivolve
current-context: sa
EOF

echo "wrote /tmp/sa.kubeconfig for system:serviceaccount:ivolve:jenkinssa"
