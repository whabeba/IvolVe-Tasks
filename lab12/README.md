# Lab 12: Managing Configuration and Sensitive Data with ConfigMaps and Secrets

## Overview
This lab covers the management of non-sensitive configuration data and sensitive credentials in Kubernetes:
- Storing non-sensitive MySQL database configuration variables using a Kubernetes `ConfigMap`.
- Encoding sensitive credentials using Base64 and storing them inside a Kubernetes `Secret`.
- Verifying the creation and metadata of both the ConfigMap and the Secret.
- Decoding Secret data from the cluster to ensure accuracy.
- Applying security best practices for Git and GitHub using environment variable templates (`.env.example`) and `.gitignore`.
- Cleaning up resources by deleting the namespace.

---

## Lab Objectives
1. Create a ConfigMap named `ivolvecm` in the `ivolve` namespace to store non-sensitive configuration variables:
   - `DB_HOST`: The hostname of the MySQL StatefulSet's headless Service.
   - `DB_USER`: The application database user authorized to connect to the database.
2. Create a Secret named `ivolvesecret` in the `ivolve` namespace to store sensitive credentials:
   - `MYSQL_ROOT_PASSWORD`: The root password for the MySQL database.
   - `DB_PASSWORD`: The application user password.
3. Use Base64 encoding to encode the Secret values for the YAML manifest.
4. Verify the resources and decode the Secret data to confirm correctness.
5. Clean up cluster resources by removing the `ivolve` namespace.

---

## Configuration Files

### 1. ConfigMap Manifest (`configmap.yaml`)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ivolvecm
  namespace: ivolve
data:
  DB_HOST: "mysql-headless.ivolve.svc.cluster.local"
  DB_USER: "ivolve_user"
```

### 2. Secret Manifest (`secret.yaml`)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ivolvesecret
  namespace: ivolve
type: Opaque
data:
  MYSQL_ROOT_PASSWORD: cm9vdHBhc3MxMjM=
  DB_PASSWORD: aXZvbHZlcGFzczEyMw==
```

### 3. Environment Security Files (`.env` and `.env.example`)
To ensure sensitive data is not tracked or leaked on GitHub:
- `.env` (Ignored via `.gitignore`):
  ```env
  MYSQL_ROOT_PASSWORD=rootpass123
  DB_PASSWORD=ivolvepass123
  ```
- `.env.example` (Committed to GitHub as a safe reference template):
  ```env
  MYSQL_ROOT_PASSWORD=your_root_password_here
  DB_PASSWORD=your_application_password_here
  ```

---

## Step-by-Step Implementation

### Step 1: Create Namespace and Apply ConfigMap

1. Create the dedicated `ivolve` namespace:
   ```bash
   kubectl create namespace ivolve
   ```

2. Apply the ConfigMap manifest (`configmap.yaml`):
   ```bash
   kubectl apply -f configmap.yaml
   ```

Output confirms:
```
namespace/ivolve created
configmap/ivolvecm created
```

![Create Namespace and Apply ConfigMap](screenshots/Screenshot%202026-10-27%20003630.png)

---

### Step 2: Base64 Encode Root Password

Encode the `MYSQL_ROOT_PASSWORD` using Base64:
```bash
echo -n 'rootpass123' | base64
```

Generated Base64 value:
```
cm9vdHBhc3MxMjM=
```

![Base64 Encode Root Password](screenshots/Screenshot%202026-10-27%20003707.png)

---

### Step 3: Base64 Encode Database User Password

Encode the `DB_PASSWORD` using Base64:
```bash
echo -n 'ivolvepass123' | base64
```

Generated Base64 value:
```
aXZvbHZlcGFzczEyMw==
```

![Base64 Encode Database Password](screenshots/Screenshot%202026-10-27%20003733.png)

---

### Step 4: Apply Secret and Verify ConfigMap

1. Apply the Secret manifest (`secret.yaml`):
   ```bash
   kubectl apply -f secret.yaml
   ```

2. Verify the ConfigMap details:
   ```bash
   kubectl get configmap -n ivolve
   kubectl describe configmap ivolvecm -n ivolve
   ```

Output confirms the data entries:
- `DB_HOST`: `mysql-headless.ivolve.svc.cluster.local`
- `DB_USER`: `ivolve_user`

![Apply Secret and Describe ConfigMap](screenshots/Screenshot%202026-10-27%20003800.png)

---

### Step 5: Verify the Secret

Inspect the Secret resource inside the `ivolve` namespace:
```bash
kubectl get secret -n ivolve
kubectl describe secret ivolvesecret -n ivolve
```

Output highlights:
- **Type**: `Opaque`
- **Data**: `DB_PASSWORD` (13 bytes), `MYSQL_ROOT_PASSWORD` (11 bytes)

![Verify Secret with kubectl describe](screenshots/Screenshot%202026-10-27%20003837.png)

---

### Step 6: Decode Secret to Validate Stored Data

Verify that the stored Base64 Secret decodes back to the original database password:
```bash
kubectl get secret ivolvesecret -n ivolve -o jsonpath="{.data.DB_PASSWORD}" | base64 --decode
echo ""
```

Output:
```
ivolvepass123
```

![Decode Secret Value](screenshots/Screenshot%202026-10-27%20003915.png)

---

### Step 7: Clean Up Resources

Delete the `ivolve` namespace to remove all created resources:
```bash
kubectl delete namespace ivolve
```

Output:
```
namespace "ivolve" deleted
```

![Delete Namespace Cleanup](screenshots/Screenshot%202026-10-27%20003937.png)
