#!/usr/bin/env bash
# =============================================================================
# Lab 23 - executable test cases (TC-01 .. TC-15)
#
# Read-only by default. `--drift` enables the two destructive checks
# (TC-08 self-heal, TC-13 drift correction) which deliberately break the cluster
# and rely on Argo CD to revert it.
#
#   bash gitops/tests/verify.sh            # safe, a few seconds
#   bash gitops/tests/verify.sh --drift    # also proves the cluster self-heals
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ ! -d "$REPO_ROOT/gitops/manifests/base" ]]; then
  echo "error: cannot find gitops/manifests/base - run this script from the repository" >&2
  echo "       bash gitops/tests/verify.sh" >&2
  exit 2
fi

NS_APP="${NS_APP:-ivolve}"
NS_ARGOCD="${NS_ARGOCD:-argocd}"
APP="${APP:-ivolve}"

DRIFT=0
[[ "${1:-}" == "--drift" ]] && DRIFT=1

pass=0
fail=0
skip=0

result() { # <id> <description> <PASS|FAIL|SKIP> <detail>
  case "$3" in
    PASS) pass=$((pass + 1)); printf '  \033[32mPASS\033[0m  %-7s %-40s %s\n' "$1" "$2" "${4:-}" ;;
    FAIL) fail=$((fail + 1)); printf '  \033[31mFAIL\033[0m  %-7s %-40s %s\n' "$1" "$2" "${4:-}" ;;
    SKIP) skip=$((skip + 1)); printf '  \033[33mSKIP\033[0m  %-7s %-40s %s\n' "$1" "$2" "${4:-}" ;;
  esac
}

k() { timeout 60 kubectl "$@" 2>/dev/null; }

echo
echo "Lab 23 - GitOps with Argo CD"
echo "context: $(k config current-context)   app: $NS_ARGOCD/$APP -> $NS_APP"
echo "-------------------------------------------------------------------------------"

# --- TC-01: every Argo CD component is running ---------------------------------
total=$(k -n "$NS_ARGOCD" get pods --no-headers | wc -l)
ready=$(k -n "$NS_ARGOCD" get pods --no-headers |
        awk '$2 ~ /^[0-9]+\/[0-9]+$/ { split($2, a, "/"); if (a[1] == a[2]) n++ } END { print n + 0 }')
if [[ "$total" -ge 7 && "$ready" -eq "$total" ]]; then
  result TC-01 "Argo CD components running" PASS "$ready/$total ready"
else
  result TC-01 "Argo CD components running" FAIL "$ready/$total ready"
fi

# --- TC-02: the UI is served ----------------------------------------------------
if k -n "$NS_ARGOCD" get svc argocd-server >/dev/null; then
  ports=$(k -n "$NS_ARGOCD" get svc argocd-server -o jsonpath='{.spec.ports[*].name}')
  result TC-02 "argocd-server service exposed" PASS "ports: $ports"
else
  result TC-02 "argocd-server service exposed" FAIL "service not found"
fi

# --- TC-03: admin credential exists --------------------------------------------
if k -n "$NS_ARGOCD" get secret argocd-initial-admin-secret >/dev/null ||
   k -n "$NS_ARGOCD" get secret argocd-secret >/dev/null; then
  result TC-03 "admin credential present" PASS "argocd-secret"
else
  result TC-03 "admin credential present" FAIL "no admin secret"
fi

# --- TC-04: repository access ----------------------------------------------------
result TC-04 "Repository reachable" SKIP "public repo - no credential entry needed"

# --- TC-05: Application exists and is Synced + Healthy --------------------------
sync=$(k -n "$NS_ARGOCD" get application "$APP" -o jsonpath='{.status.sync.status}')
health=$(k -n "$NS_ARGOCD" get application "$APP" -o jsonpath='{.status.health.status}')
rev=$(k -n "$NS_ARGOCD" get application "$APP" -o jsonpath='{.status.sync.revision}')
if [[ "$sync" == "Synced" && "$health" == "Healthy" ]]; then
  result TC-05 "Application Synced + Healthy" PASS "rev ${rev:0:8}"
else
  result TC-05 "Application Synced + Healthy" FAIL "${sync:-?}/${health:-?} rev ${rev:0:8}"
fi

# --- TC-06: the live cluster matches Git ----------------------------------------
manifest=$(kubectl kustomize "$REPO_ROOT/gitops/manifests/base" 2>/dev/null)
# `image:` is printed as a list item ("- image: repo:tag"), so strip the prefix.
want_img=$(printf '%s\n' "$manifest" |
           grep -E '^[[:space:]]*-?[[:space:]]*image:' | head -1 |
           sed -E 's/.*image:[[:space:]]*//' | tr -d '"')
want_rep=$(printf '%s\n' "$manifest" | awk '/^[[:space:]]+replicas:/ { print $2; exit }')

got_img=$(k -n "$NS_APP" get deploy "$APP" -o jsonpath='{.spec.template.spec.containers[0].image}')
if [[ -n "$want_img" && "$want_img" == "$got_img" ]]; then
  result TC-06.1 "Deployed image == Git image" PASS "$got_img"
else
  result TC-06.1 "Deployed image == Git image" FAIL "git=$want_img cluster=$got_img"
fi

got_rep=$(k -n "$NS_APP" get deploy "$APP" -o jsonpath='{.status.availableReplicas}')
if [[ -n "$want_rep" && "$want_rep" == "$got_rep" ]]; then
  result TC-06.2 "Deployment fully available" PASS "$got_rep/$want_rep replicas"
else
  result TC-06.2 "Deployment fully available" FAIL "available=${got_rep:-0} want=$want_rep"
fi

policy=$(k -n "$NS_ARGOCD" get application "$APP" -o jsonpath='{.spec.syncPolicy.automated}')
if [[ "$policy" == *'"prune":true'* && "$policy" == *'"selfHeal":true'* ]]; then
  result TC-06.3 "Automated sync + prune + selfHeal" PASS "$policy"
else
  result TC-06.3 "Automated sync + prune + selfHeal" FAIL "${policy:-unset}"
fi

eps=$(k -n "$NS_APP" get endpoints "$APP" -o jsonpath='{.subsets[*].addresses[*].ip}')
if [[ -n "$eps" ]]; then
  result TC-06.4 "Service has ready endpoints" PASS "$(printf '%s\n' "$eps" | wc -w) pod(s)"
else
  result TC-06.4 "Service has ready endpoints" FAIL "no ready endpoints"
fi

# --- tests that need a pushed commit or a CI run --------------------------------
result TC-07 "Auto-sync on Git change" SKIP "needs: edit + git push - see README"
result TC-09 "Prune deleted resource" SKIP "needs: edit + git push - see README"
result TC-10 "CI builds and pushes image" SKIP "runs in GitHub Actions - see README"
result TC-11 "CI only changes newTag" SKIP "runs in GitHub Actions - see README"
result TC-12 "End-to-end rollout" SKIP "runs in GitHub Actions - see README"
result TC-15 "Fail-safe CI" SKIP "runs in GitHub Actions - see README"

# --- TC-14: the CI identity has no cluster power --------------------------------
can=$(k auth can-i delete deployments -n "$NS_APP" \
      --as=system:serviceaccount:"$NS_APP":jenkinssa)
if [[ "$can" == "no" ]]; then
  result TC-14 "CI cannot delete Deployments" PASS "denied by RBAC"
else
  result TC-14 "CI cannot delete Deployments" FAIL "got: ${can:-empty}"
fi

# --- destructive checks ---------------------------------------------------------
if [[ "$DRIFT" -eq 1 && -n "$want_rep" ]]; then
  echo "-------------------------------------------------------------------------------"
  echo "  drift tests - Argo CD should revert both changes in < 120s"
  echo

  # TC-08: self-heal on replicas
  target=$((want_rep + 3))
  k -n "$NS_APP" scale deploy "$APP" --replicas="$target" >/dev/null
  ok=0
  for _ in $(seq 1 24); do
    now=$(k -n "$NS_APP" get deploy "$APP" -o jsonpath='{.spec.replicas}')
    [[ "$now" == "$want_rep" ]] && { ok=1; break; }
    sleep 5
  done
  if [[ "$ok" -eq 1 ]]; then
    result TC-08 "Self-heal reverts a manual scale" PASS "scaled to $target, back to $want_rep"
  else
    result TC-08 "Self-heal reverts a manual scale" FAIL "still at ${now:-?} replicas"
  fi

  # TC-13: self-heal on the image
  k -n "$NS_APP" set image deploy/"$APP" app=nginx:1.25 >/dev/null
  ok=0
  for _ in $(seq 1 24); do
    now=$(k -n "$NS_APP" get deploy "$APP" -o jsonpath='{.spec.template.spec.containers[0].image}')
    [[ "$now" == "$want_img" ]] && { ok=1; break; }
    sleep 5
  done
  if [[ "$ok" -eq 1 ]]; then
    result TC-13 "Self-heal reverts a manual image" PASS "restored $want_img"
  else
    result TC-13 "Self-heal reverts a manual image" FAIL "still at ${now:-?}"
  fi
else
  result TC-08 "Self-heal reverts a manual scale" SKIP "run with --drift"
  result TC-13 "Self-heal reverts a manual image" SKIP "run with --drift"
fi

# --- summary --------------------------------------------------------------------
echo "-------------------------------------------------------------------------------"
printf '  %d passed, %d failed, %d skipped\n\n' "$pass" "$fail" "$skip"
[[ "$fail" -eq 0 ]] || exit 1
