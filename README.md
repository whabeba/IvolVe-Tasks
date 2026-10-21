# iVolve Training — DevOps Labs

Hands-on DevOps labs covering containerization, orchestration, infrastructure as code, CI/CD pipelines, and configuration management.

---

## Table of Contents

- [Overview](#overview)
- [Technologies Covered](#technologies-covered)
- [Labs](#labs)
- [Getting Started](#getting-started)

---

## Overview

This repository contains practical labs completed as part of the iVolve DevOps training program. Each lab focuses on a core DevOps tool or concept, with step-by-step implementation, screenshots, and documented results.

---

## Technologies Covered

| Technology | Category |
|-----------|----------|
| Docker | Containerization |
| Kubernetes (K8s) | Container Orchestration |
| Ansible | Configuration Management |
| Jenkins | CI/CD Pipelines |
| ArgoCD | GitOps / Continuous Delivery |
| Maven | Build Automation |
| Terraform | Infrastructure as Code |
| Git / GitHub | Version Control |
| Linux | Operating System |

---

## Labs

### Docker — Containerization with Docker

| Lab | Title | Key Concepts |
|-----|-------|-------------|
| [Lab 4](lab4/README.md) | Docker Image Optimization and Export/Load | Multi-stage builds, non-root user, docker save/load |
| [Lab 5](lab5/README.md) | Docker Image Vulnerability Scanning with Trivy | Trivy scan, HIGH/CRITICAL CVEs, base image remediation, HTML report |
| [Lab 6](lab6/README.md) | Docker Environment Variables and Resource Management | ENV variables, --env-file, hardcoded ENV, CPU/memory limits |

---

### Lab 4 — Docker Image Optimization and Export/Load

**Goal:** Optimize a Docker image using multi-stage builds and run the app as a non-root user.

**What was done:**
- Built a Spring Boot app image from an existing single-stage Dockerfile (image1 — 671 MB)
- Wrote a multi-stage Dockerfile using a JRE-only base image and a non-root user
- Built the optimized image (image2 — 340 MB) — 50% size reduction
- Exported image2 as a TAR file, deleted it, and restored it using docker load

**Key commands:**
```bash
docker build -t image1 .
docker build -t image2 .
docker images | grep -E "image1|image2"
docker save -o lab-image.tar image2
docker rmi image2
docker load -i lab-image.tar
```

[View Lab 4 README](lab4/README.md)

---

### Lab 5 — Docker Image Vulnerability Scanning with Trivy

**Goal:** Scan a Docker image for vulnerabilities and fix them by updating the base image.

**What was done:**
- Built a Node.js app image using node:18-bullseye (12,478 vulnerabilities found)
- Installed Trivy and scanned for HIGH and CRITICAL vulnerabilities (222 CRITICAL, 2,074 HIGH)
- Generated an HTML vulnerability report with charts using Python/matplotlib
- Fixed the base image by switching from node:18-bullseye to node:18-alpine
- Rescanned the updated image and confirmed significant vulnerability reduction

**Key commands:**
```bash
trivy image trivy-lab:v1
trivy image --severity HIGH,CRITICAL trivy-lab:v1
trivy image --format json -o trivy-report.json trivy-lab:v1
python3 generate_report.py
```

**Vulnerability comparison:**

| Severity | v1 (bullseye) | v2 (alpine) |
|----------|--------------|-------------|
| CRITICAL | 222 | reduced |
| HIGH | 2,074 | reduced |
| TOTAL | 12,478 | much less |

[View Lab 5 README](lab5/README.md)

---

### Lab 6 — Docker Environment Variables and Resource Management

**Goal:** Demonstrate three different ways to pass environment variables to Docker containers and apply resource limits.

**What was done:**
- Built a Python Flask app image using python:3.12-slim
- Ran container1 with ENV variables passed via -e flags and limited to 1 CPU / 256MB memory
- Ran container2 loading ENV variables from an env.txt file
- Created a new Dockerfile with hardcoded ENV variables and ran container3

**Three methods of setting ENV variables:**

| Method | Command | Use Case |
|--------|---------|---------|
| Runtime flags | `-e APP_NAME=value` | Quick testing |
| Env file | `--env-file env.txt` | Multiple variables |
| Dockerfile ENV | `ENV APP_NAME=value` | Fixed default values |

**Resource limits:**
```bash
docker run --cpus="1" --memory="256m" ...
docker stats container1 --no-stream
```

[View Lab 6 README](lab6/README.md)

---

## Getting Started

### Prerequisites

- Docker installed and running
- Git installed
- Linux or WSL environment

### Clone this repository

```bash
git clone https://github.com/whabeba/IvolVe-Tasks.git
cd IvolVe-Tasks
```

### Navigate to a lab

```bash
cd lab4/ImageOptimization-
cd lab5/TrivyImage
cd lab6/PythonApp
```

---

## Repository Structure

```
IvolVe-Tasks/
├── lab4/
│   ├── ImageOptimization-/
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── pom.xml
│   ├── screenshots/
│   └── README.md
├── lab5/
│   ├── TrivyImage/
│   │   ├── Dockerfile
│   │   ├── Dockerfile.v2
│   │   ├── app.js
│   │   ├── package.json
│   │   ├── generate_report.py
│   │   ├── analyze_vulnerabilities.py
│   │   └── screenshots/
│   ├── screen shots/
│   └── README.md
├── lab6/
│   ├── PythonApp/
│   │   ├── Dockerfile
│   │   ├── Dockerfile.v2
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── screenshots/
│   └── README.md
└── README.md
```

---

*iVolve Technology — DevOps Training Program*
