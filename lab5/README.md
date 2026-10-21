# Lab 5: Docker Image Vulnerability Scanning with Trivy

A Node.js application used to demonstrate Docker image vulnerability scanning using Trivy, including remediation by updating the base image and generating analysis reports.

---

## Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Ibrahim-Adel15/TrivyImage.git
cd TrivyImage
```

---

### 2. Build the Docker image and tag it as trivy-lab:v1

```bash
docker build -t trivy-lab:v1 .
```

---

### 3. Install Trivy and verify the installation

```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list

sudo apt-get update
sudo apt-get install trivy -y

trivy --version
```

![Trivy Installation](screenshots/trivydownload.png)

> Trivy version 0.71.2 installed successfully

---

### 4. Scan the Docker image for vulnerabilities

```bash
trivy image --format json -o trivy-report.json trivy-lab:v1
```

![Scan trivy-lab:v1](screenshots/trivyreport.png)

> Detected OS: debian family version 11.11 with 409 packages scanned

---

### 5. Scan the image to identify only HIGH and CRITICAL vulnerabilities

```bash
trivy image --severity HIGH,CRITICAL trivy-lab:v1
```

---

### 6. Generate an HTML vulnerability report

```bash
trivy image --format template --template "@$HOME/.trivy/contrib/html.tpl" --output trivy-report.html trivy-lab:v1
```

---

### 7. Vulnerability Analysis — v1 Results

Total vulnerabilities found in trivy-lab:v1 (node:18-bullseye):

| Severity | Count |
|----------|-------|
| CRITICAL | 222 |
| HIGH | 2,074 |
| MEDIUM | 7,013 |
| LOW | 3,066 |
| UNKNOWN | 103 |
| **TOTAL** | **12,478** |

![Bar Chart - v1](screenshots/bar_chart.png)

![Pie Chart - v1](screenshots/pie_chart.png)

![Top 10 Critical CVEs](screenshots/top10_cves.png)

---

## Bonus: Vulnerability Remediation

### 8. Investigate the vulnerabilities and fix the Dockerfile

The root cause of most vulnerabilities was the base image `node:18-bullseye` which is based on Debian 11 and includes over 400 system packages, each a potential source of CVEs.

Fix: Replace the base image with `node:18-alpine` which uses Alpine Linux with only ~15 packages.

```dockerfile
# Before
FROM node:18-bullseye

# After
FROM node:18-alpine
```

---

### 9. Rebuild the Docker image and tag it as ivolve-app:v2

```bash
docker build -t ivolve-app:v2 .
```

---

### 10. Rescan the updated image and generate a new report

```bash
trivy image --format json -o trivy-report-v2.json ivolve-app:v2
```

![Scan ivolve-app:v2 and generate report](screenshots/scanV2.png)

> Detected OS changed from debian to alpine family version 3.21.3 with only 17 packages

---

### 11. Vulnerability Comparison — v1 vs v2

```bash
python3 generate_report.py
```

![Comparison Chart - HIGH and CRITICAL](screenshots/comparison_chart.png)

![Pie Chart - v2](screenshots/pie_chart_v2.png)

| Severity | v1 (node:18-bullseye) | v2 (node:18-alpine) | Change |
|----------|-----------------------|----------------------|--------|
| CRITICAL | 222 | reduced | down |
| HIGH | 2,074 | reduced | down |
| MEDIUM | 7,013 | reduced | down |
| LOW | 3,066 | reduced | down |
| TOTAL | 12,478 | much less | down |

> Switching from Debian-based to Alpine-based image significantly reduced the number of vulnerabilities because Alpine ships with far fewer system packages.

---

## Summary

| Step | Action | Result |
|------|--------|--------|
| Build trivy-lab:v1 | node:18-bullseye base image | 12,478 vulnerabilities |
| Install Trivy | version 0.71.2 | Scan tool ready |
| Scan v1 | Full vulnerability scan | 222 CRITICAL, 2074 HIGH |
| Fix Dockerfile | Changed base to node:18-alpine | Fewer system packages |
| Build ivolve-app:v2 | Alpine-based image | Vulnerabilities reduced |
| Generate report | Python analysis script | HTML report + PNG charts |
