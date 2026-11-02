# Lab 13: Persistent Storage Setup for Application Logging

## Overview

This lab demonstrates setting up Kubernetes persistent storage for application logging using a statically provisioned PersistentVolume (PV) with `hostPath` and a PersistentVolumeClaim (PVC).

## Objectives

1. Define a PersistentVolume (`ivolvepv`) with:
   - Capacity: `1Gi`
   - Access Mode: `ReadWriteMany` (RWX)
   - Reclaim Policy: `Retain`
   - Storage Type: `hostPath` at `/mnt/app-logs` on the node filesystem
   - StorageClass: None (`""`)
2. Define a PersistentVolumeClaim (`ivolvepvc`) with:
   - Requested Storage: `1Gi`
   - Access Mode: `ReadWriteMany`
   - StorageClass: None (`""`)
3. Validate binding between the PV and PVC.
4. Verify data persistence by mounting the PVC into a test Pod and inspecting the log files on the host node.

---

## File Structure

- `pv.yaml`: Defines the PersistentVolume specification.
- `pvc.yaml`: Defines the PersistentVolumeClaim specification.
- `test-pod.yaml`: Test Pod manifest to mount the PVC and generate application logs.
- `screenshots/`: Contains execution and verification evidence.

---

## Manifest Definitions

### 1. PersistentVolume (`pv.yaml`)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ivolvepv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  hostPath:
    path: /mnt/app-logs
    type: DirectoryOrCreate
```

### 2. PersistentVolumeClaim (`pvc.yaml`)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ivolvepvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: ""
  resources:
    requests:
      storage: 1Gi
```

### 3. Test Pod (`test-pod.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: logging-test
spec:
  containers:
    - name: logger
      image: busybox:1.36
      command: ["sh", "-c", "echo 'Lab 13 logging test' > /logs/app.log; sleep 3600"]
      volumeMounts:
        - name: logs
          mountPath: /logs
  volumes:
    - name: logs
      persistentVolumeClaim:
        claimName: ivolvepvc
```

---

## Steps and Verification

### Step 1: Apply PV and PVC Manifests

Apply the manifests to create the PersistentVolume and PersistentVolumeClaim:

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
```

![Apply PV and PVC](screenshots/Screenshot%202026-10-28%20234650.png)

---

### Step 2: Verify Status of PV and PVC

Verify that both the PV and PVC have been successfully bound:

```bash
kubectl get pv
kubectl get pvc
```

Both resources report a `Bound` status. The PVC `ivolvepvc` is bound to volume `ivolvepv` with `1Gi` capacity and `RWX` access mode.

![Get PV and PVC](screenshots/Screenshot%202026-10-28%20234717.png)

---

### Step 3: Inspect PersistentVolume Details

Inspect detailed configuration attributes of the PersistentVolume:

```bash
kubectl describe pv ivolvepv
```

The output confirms:
- Status: `Bound`
- Claim: `default/ivolvepvc`
- Reclaim Policy: `Retain`
- Access Modes: `RWX`
- Capacity: `1Gi`
- Source Path: `/mnt/app-logs`

![Describe PV](screenshots/Screenshot%202026-10-28%20234739.png)

---

### Step 4: Check Node Filesystem Prior to Pod Mount

Check the status of `/mnt/app-logs` on the Minikube node before running the workload:

```bash
minikube ssh
ls -ld /mnt/app-logs
exit
```

Because `hostPath` with `type: DirectoryOrCreate` creates the directory on the host when the Pod mounts the volume, the directory is not yet created prior to Pod deployment.

![Check Node Before Pod](screenshots/Screenshot%202026-10-28%20234809.png)

---

### Step 5: Deploy Test Pod and Write Application Logs

Deploy the test Pod to mount the PVC at `/logs` and write an entry to `/logs/app.log`:

```bash
kubectl apply -f test-pod.yaml
kubectl wait --for=condition=Ready pod/logging-test --timeout=120s
kubectl exec logging-test -- cat /logs/app.log
```

The log entry `Lab 13 logging test` is verified inside the running container.

![Deploy Test Pod](screenshots/Screenshot%202026-10-28%20234945.png)

---

### Step 6: Verify Persistence on the Minikube Host Node

SSH into the Minikube node to confirm that the log file persists in the host directory `/mnt/app-logs`:

```bash
minikube ssh
ls -l /mnt/app-logs
cat /mnt/app-logs/app.log
exit
```

The file `app.log` exists in `/mnt/app-logs/` with the content `Lab 13 logging test`.

![Verify Node Persistence](screenshots/Screenshot%202026-10-28%20235014.png)

---

### Step 7: Clean Up Test Pod

Delete the test pod to ensure the volume and its underlying logs remain intact on the host:

```bash
kubectl delete pod logging-test
```

![Delete Test Pod](screenshots/Screenshot%202026-10-28%20235127.png)

---

## Conclusion

The persistent storage configuration for application logging was successfully established and verified. The `hostPath` volume retains log files on the host node independently of the Pod lifecycle.
