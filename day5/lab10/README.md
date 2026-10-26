# Lab 10: Node Isolation Using Taints and Labels in Kubernetes

## Overview
This lab demonstrates node isolation and workload placement control in Kubernetes using node taints and labels:
- Apply a taint to prevent pods from being scheduled on a node without matching tolerations.
- Add labels to a node to identify it for targeted pod scheduling using node selectors or node affinity.
- Verify the applied taints and labels using `kubectl` inspection commands.
- Remove the taint as part of cleanup.

---

## Lab Objectives
1. Apply a taint with key `workload`, value `ivolveApp`, and effect `NoSchedule` to the node.
2. Label the node with `project=ivolve`.
3. Verify that the taint and label were applied successfully using `kubectl describe node` and `kubectl get nodes --show-labels`.
4. Remove the applied taint (cleanup).

---

## Step-by-Step Implementation

### Step 1: Check Nodes, Apply Taint, and Assign Label

1. Check existing cluster nodes:
   ```bash
   kubectl get nodes
   ```

2. Apply a taint to the node (`minikube`) to repel pods without tolerations:
   ```bash
   kubectl taint node minikube workload=ivolveApp:NoSchedule
   ```

3. Label the node (`minikube`) with `project=ivolve` for targeted workload assignment:
   ```bash
   kubectl label node minikube project=ivolve
   ```

![Applying Taint and Label to Node](screenshots/Screenshot%202026-10-26%20225817.png)

---

### Step 2: Verify Taints and Labels via Node Description

Verify that the taint and label have been recorded in the node specification:
```bash
kubectl describe node minikube
```

Expected Output Highlights:
- **Labels**: includes `project=ivolve`
- **Taints**: includes `workload=ivolveApp:NoSchedule`

![Verifying Taint and Label via kubectl describe](screenshots/Screenshot%202026-10-26%20225912.png)

---

### Step 3: Verify Labels Using `--show-labels`

Check all node labels in tabular format:
```bash
kubectl get nodes --show-labels
```

The output confirms the presence of `project=ivolve` under the `LABELS` column.

![Verifying Node Labels](screenshots/Screenshot%202026-10-26%20225950.png)

---

### Step 4: Remove the Taint (Cleanup)

To allow general pods to schedule on the node again, remove the taint by appending a minus sign (`-`) to the key/effect:
```bash
kubectl taint node minikube workload=ivolveApp:NoSchedule-
```

Output:
```
node/minikube untainted
```

![Removing Taint from Node](screenshots/Screenshot%202026-10-26%20230021.png)
