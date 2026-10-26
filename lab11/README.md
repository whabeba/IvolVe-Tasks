# Lab 11: Namespace Management and Resource Quota Enforcement

## Overview
This lab demonstrates multi-tenancy resource management and isolation in Kubernetes:
- Creating a dedicated namespace for application isolation.
- Enforcing resource constraints using a `ResourceQuota` to limit total pod creation.
- Verifying quota status before and after workload deployment.
- Testing quota enforcement and confirming Kubernetes prevents additional pod creation when limits are reached.
- Cleaning up resources by removing the created namespace.

---

## Lab Objectives
1. Create a Kubernetes namespace named `ivolve` to isolate application resources.
2. Create a ResourceQuota named `ivolvequota` in the `ivolve` namespace to limit the total number of pods to 3.
3. Verify that the ResourceQuota is applied correctly.
4. Confirm that Kubernetes prevents the creation of additional pods once the limit (3 pods) is reached.
5. Clean up cluster resources by deleting the `ivolve` namespace.

---

## Configuration Files

### ResourceQuota Definition (`quota.yaml`)
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ivolvequota
  namespace: ivolve
spec:
  hard:
    pods: "3"
```

---

## Step-by-Step Implementation

### Step 1: Create and Verify the Namespace

1. Check existing cluster nodes:
   ```bash
   kubectl get nodes
   ```

2. Create the dedicated `ivolve` namespace:
   ```bash
   kubectl create namespace ivolve
   ```

3. Confirm that the namespace was successfully created:
   ```bash
   kubectl get namespaces
   ```

![Create and Verify Namespace](screenshots/Screenshot%202026-10-26%20235757.png)

---

### Step 2: Apply the ResourceQuota

Apply the `quota.yaml` manifest to enforce a maximum of 3 pods inside the `ivolve` namespace, then verify the quota resource:

```bash
kubectl apply -f quota.yaml
kubectl get quota -n ivolve
```

Expected Output:
```
NAME          REQUEST     LIMIT   AGE
ivolvequota   pods: 0/3           16s
```

![Apply ResourceQuota and Get Quota](screenshots/Screenshot%202026-10-26%20235850.png)

---

### Step 3: Inspect Initial Quota State

Inspect the newly created ResourceQuota details before launching any pods:

```bash
kubectl describe quota ivolvequota -n ivolve
```

Output confirms that 0 out of 3 hard limits are currently consumed:
- **Resource**: `pods`
- **Used**: `0`
- **Hard**: `3`

![Initial Quota Inspection](screenshots/Screenshot%202026-10-26%20235925.png)

---

### Step 4: Deploy Workload to Reach Quota Limit

Create a deployment with 3 replicas to reach the maximum pod quota limit:

```bash
kubectl create deployment test-deploy --image=nginx --replicas=3 -n ivolve
```

![Deploy 3 Replicas](screenshots/Screenshot%202026-10-26%20235955.png)

---

### Step 5: Verify Quota Saturation and Test Enforcement

1. Inspect the quota again to verify that all 3 allowed pods are running:
   ```bash
   kubectl describe quota ivolvequota -n ivolve
   ```
   Output confirms: `Used: 3 / Hard: 3`.

2. Attempt to create a 4th standalone pod:
   ```bash
   kubectl run pod-extra --image=nginx -n ivolve
   ```
   Result: The API server immediately rejects the request with a Forbidden error:
   ```
   Error from server (Forbidden): pods "pod-extra" is forbidden: exceeded quota: ivolvequota, requested: pods=1, used: pods=3, limited: pods=3
   ```

3. Attempt to scale the deployment to 4 replicas:
   ```bash
   kubectl scale deployment test-deploy --replicas=4 -n ivolve
   ```

![Quota Saturation and Rejection of 4th Pod](screenshots/Screenshot%202026-10-27%20000030.png)

---

### Step 6: Verify Deployment Events for Failed Pod Creation

Inspect cluster events to confirm that the ReplicaSet was blocked from creating the 4th replica due to the quota limit:

```bash
kubectl get events -n ivolve --sort-by='.metadata.creationTimestamp'
```

Output shows `FailedCreate` events indicating that additional pods were blocked:
```
Warning  FailedCreate  replicaset/test-deploy-84d9966d59  Error creating: pods "test-deploy-84d9966d59-..." is forbidden: exceeded quota: ivolvequota, requested: pods=1, used: pods=3, limited: pods=3
```

![Cluster Events Showing Quota Enforcement](screenshots/Screenshot%202026-10-27%20000057.png)

---

### Step 7: Clean Up Resources

Delete the `ivolve` namespace to remove all contained resources (deployments, pods, and resourcequotas):

```bash
kubectl delete namespace ivolve
```

Output:
```
namespace "ivolve" deleted
```

![Namespace Deletion and Cleanup](screenshots/Screenshot%202026-10-27%20000153.png)
