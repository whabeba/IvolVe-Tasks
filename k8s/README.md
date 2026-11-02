# Kubernetes Labs

Hands-on Kubernetes labs, from bootstrapping a cluster with `kubeadm` to securing workloads with RBAC.

Each lab is a self-contained folder with manifests, a step-by-step `README.md`, and terminal screenshots showing the actual result of every command. The labs build on each other: they start with a bare cluster, add scheduling rules and configuration, deploy a stateful database and a stateless application, then layer on storage, networking, monitoring and access control.

| # | Lab | Focus | Key resources |
|---|---|---|---|
| 9 | [Deploy a Kubernetes Cluster with kubeadm](lab9/README.md) | Manual cluster bootstrap on AWS EC2 (1 control plane + 1 worker, containerd, Calico) | `kubeadm`, `kubelet`, `kubectl`, Calico |
| 10 | [Node Isolation with Taints and Labels](lab10/README.md) | Control *where* Pods land, and repel the ones that do not belong | taints, tolerations, labels, `nodeSelector` |
| 11 | [Namespace Management and Resource Quota](lab11/README.md) | Multi-tenancy: isolate a team and cap how much it can consume | `Namespace`, `ResourceQuota` |
| 12 | [ConfigMaps and Secrets](lab12/README.md) | Move configuration out of the image, keep credentials out of Git | `ConfigMap`, `Secret`, `.env` / `.gitignore` |
| 13 | [Persistent Storage for Application Logs](lab13/README.md) | Data that survives Pod restarts | `PersistentVolume`, `PersistentVolumeClaim` |
| 14 | [StatefulSet with a Headless Service](lab14/README.md) | Run MySQL with a stable identity, stable DNS and stable storage | `StatefulSet`, headless `Service`, `Secret` |
| 15 | [Node.js App with a ClusterIP Service](lab15/README.md) | Deploy the application tier and wire it to the database | `Deployment`, `ClusterIP`, init container |
| 16 | [CPU and Memory Requests and Limits](lab16/README.md) | Give the scheduler a floor and the runtime a ceiling | requests, limits, QoS classes |
| 17 | [Pod-to-Pod Traffic with NetworkPolicy](lab17/README.md) | Default-deny the database; allow only its client | `NetworkPolicy` (enforced by Calico) |
| 18 | [Node-Wide Pods with a DaemonSet](lab18/README.md) | A monitoring stack: one exporter per node, plus Prometheus, Alertmanager and Grafana | `DaemonSet`, `Deployment`, `ConfigMap`, RBAC |
| 19 | [RBAC and Service Accounts](lab19/README.md) | Let a CI runner deploy without making it cluster-admin | `ServiceAccount`, `Role`, `RoleBinding`, token |

---

## Repository layout

```
.
├── lab9/                  # kubeadm cluster on AWS EC2
├── lab10/                 # taints, labels and workload placement
├── lab11/                 # namespace + resource quota
├── lab12/                 # ConfigMap, Secret, .env hygiene
├── lab13/                 # PersistentVolume + PersistentVolumeClaim
├── lab14/                 # MySQL StatefulSet + headless Service
├── lab15/                 # Node.js Deployment + ClusterIP Service
├── lab16/                 # resource requests and limits
├── lab17/                 # NetworkPolicy (Calico)
├── lab18/                 # node-exporter DaemonSet + Prometheus/Alertmanager/Grafana
└── lab19/                 # ServiceAccount + Role + RoleBinding
```

Every lab folder follows the same shape:

```
labN/
├── README.md              # the lab: what it proves, then step → screenshot
├── 00-*.yaml              # numbered manifests, applied in order
└── screenshots/           # proof of each step
```

Labs that need a credential ship an `*.example.yaml` with placeholders instead of the real value (see [Security notes](#security-notes)).

---

## Prerequisites

**Tools**

- Docker Desktop (or Docker Engine)
- `minikube` v1.38.1
- `kubectl`
- `git` and a bash shell (WSL on Windows works fine)
- Optional: a MySQL client for Lab 14

**Cluster used for Labs 10–19**

| Item | Version |
|---|---|
| Kubernetes | v1.35.1 |
| minikube | v1.38.1 (docker driver) |
| CNI | Calico v3.31.3 |
| Node | `minikube` (192.168.49.2) |

**Lab 9** is the exception: it is built on two AWS EC2 instances (Ubuntu 22.04, `kubeadm` v1.29.15) and needs an AWS account and two VMs, not minikube.

---

## Getting started

```bash
git clone https://github.com/whabeba/k8s.git
cd k8s
```

Start a cluster with a CNI that actually enforces NetworkPolicy (required by Lab 17):

```bash
minikube start --driver=docker --cpus=2 --memory=3072 --cni=calico
kubectl get nodes
kubectl get pods -n kube-system | grep calico
```

Then pick a lab and follow its `README.md`:

```bash
cd lab14
kubectl apply -f 00-namespace.yaml -f 01-configmap.yaml
# ... the README lists the remaining steps and the expected output
```

### Suggested order

Labs 14–19 form a single application stack, and Labs 11–13 provide the namespace and storage it uses. Run them in this order:

```
11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19
```

Labs 9 and 10 are standalone: Lab 9 builds the cluster itself, Lab 10 is a scheduling exercise that can run on any cluster.

---

## What each lab demonstrates

- **Lab 9 — Cluster bootstrap.** Install and configure `containerd`, `kubeadm`, `kubelet` and `kubectl` on both nodes, initialise the control plane, install Calico, join the worker, and verify that all control-plane and CNI Pods are healthy.
- **Lab 10 — Scheduling control.** Taint a node with `workload=ivolveApp:NoSchedule`, label it `project=ivolve`, then inspect the result with `kubectl describe node` and `kubectl get nodes --show-labels` before removing the taint.
- **Lab 11 — Quotas.** Create the `ivolve` namespace and a `ResourceQuota` that caps the namespace at 3 Pods; confirm that the fourth Pod is rejected by the API server, not by the scheduler.
- **Lab 12 — Configuration and secrets.** Store non-sensitive values in a `ConfigMap` and credentials in a base64 `Secret`, then prove the decode round-trip. Also covers keeping `.env` out of Git with `.gitignore` and committing `.env.example` instead.
- **Lab 13 — Persistent storage.** A statically provisioned `hostPath` PV (1Gi, `ReadWriteMany`, `Retain`) bound by a PVC, mounted into a Pod that writes logs to `/mnt/app-logs`; the file is still there after the Pod is recreated.
- **Lab 14 — Stateful workload.** MySQL 8 as a `StatefulSet` behind a headless Service, with config injected from the Lab 12 `ConfigMap`/`Secret`, a `nodeSelector` plus toleration from Lab 10, a PVC template at `/var/lib/mysql`, and DNS resolution verified from inside the cluster.
- **Lab 15 — Application tier.** The Node.js image from the Docker labs as a 2-replica `Deployment` behind a `ClusterIP` Service; an init container waits for MySQL, creates the database and grants privileges; the app reuses the Lab 13 PV for its access log.
- **Lab 16 — Resource management.** Set `requests` (1 CPU / 1Gi) and `limits` (2 CPU / 2Gi) on the app container, and read the resulting **Burstable** QoS class, scheduler behaviour and OOM/throttling semantics.
- **Lab 17 — Network policy.** Allow only `app=ivolveapp` Pods to reach the MySQL Pod on TCP 3306, and prove both the allowed and the denied path. The README explains why the default minikube `bridge` CNI had to be replaced with Calico.
- **Lab 18 — Node-wide monitoring.** `node-exporter` as a `DaemonSet` with `hostNetwork`/`hostPort 9100`, Prometheus scraping it with alert rules, Alertmanager receiving the alerts, and Grafana provisioned from ConfigMaps with a dashboard reading real data.
- **Lab 19 — Least-privilege CI identity.** A `ServiceAccount` with a long-lived token, a namespaced `Role` granting only `create` and `update` on `deployments`, and a `RoleBinding`. Validation uses a token-only kubeconfig so the results are really evaluated as the ServiceAccount.

---

## Conventions

- **Numbered manifests** (`00-`, `01-`, …) are applied in filename order; the README always shows the exact command.
- **Lowercase DNS names.** Kubernetes object names must be DNS labels, so the camelCase names from the lab sheets are written lowercase (`jenkinsSA` → `jenkinssa`, `ivolveDeployRole` → `ivolvdeployrole`). Each lab README keeps a mapping table where this matters.
- **README format:** one step → the command and a one-or-two-line explanation of what to look for → the screenshot of that command's real output.
- **Images are loaded into the node** (`minikube image load`) rather than pulled from a registry, so the labs work offline.
- **Screenshots are evidence, not decoration.** Every step has one, and each shows the command with its actual output.

---

## Security notes

These are learning labs, and the repository is public. A few rules are applied throughout:

- **No real credentials are committed.** Where a lab needs a password, the repository ships an `*.example.yaml` containing placeholders such as `REPLACE_WITH_BASE64_ROOT_PASSWORD`, and the real file is created locally and ignored by Git.
- **Grafana (Lab 18)** takes its admin password from a Kubernetes `Secret` created imperatively with `kubectl create secret`; only the shape of that Secret is published.
- **RBAC (Lab 19)** reads the ServiceAccount token from the cluster at runtime (`kubectl get secret … -o jsonpath`). No token is written to a file in this repository.
- **Lab 9** publishes the `kubeadm join` command with the bootstrap token and CA hash replaced by placeholders; the cluster and its EC2 instances were destroyed after the lab.
- **A few older screenshots** captured terminal output that contained the MySQL lab password. Those values are masked with black bars in `lab12/` and `lab14/`, and the corresponding text in the READMEs uses placeholders.

If you reuse any of this material, treat every lab credential as compromised and generate your own.

---

## Cleanup

Each lab README ends with its cleanup commands. In general:

```bash
# a single lab
kubectl delete -f <manifests> --ignore-not-found

# the shared application namespace
kubectl delete namespace ivolve

# everything, including the cluster
minikube delete
```

---

## Notes and gotchas

- **NetworkPolicy needs the right CNI.** Kubernetes stores a policy but does not enforce it; the default minikube `bridge` CNI ignores it. Lab 17 was run on Calico, and the CNI has to exist when the node is created (`minikube start --cni=calico`), not added afterwards.
- **`kubectl --token` is not enough for an RBAC test.** If the kubeconfig also contains a client certificate, kubectl keeps authenticating with the certificate. Lab 19 builds a token-only kubeconfig so every allow/deny result is genuine.
- **Requests and limits are different things.** Requests decide placement, limits are enforced by the runtime: exceeding memory gets the container OOM-killed, exceeding CPU only throttles it.
- **`hostPath` PVs are node-local.** The Lab 13/15 volume works because everything runs on the single minikube node; on a multi-node cluster you would use a real storage class.
- **StatefulSet Pod names are stable** (`ivolvedb-0`), and the headless Service gives each Pod a DNS record — that is what makes the database addressable across restarts.

---

## License

Educational material, free to reuse and adapt. See each lab README for the original assignment description.
