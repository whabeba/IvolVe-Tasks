# iVolve Training — DevOps Labs

Hands-on DevOps labs covering containerization, orchestration, infrastructure as code, CI/CD pipelines, and configuration management.

---

## Table of Contents

- [Overview](#overview)
- [Technologies Covered](#technologies-covered)# iVolve Training — DevOps Labs

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
| [Lab 7](lab7/README.md) | Multi-Network Microservices, Volumes, and Bind Mounts | Bridge networks, named volumes, bind mounts, multi-container communication |
| [Lab 8](lab8/README.md) | Containerized Node.js and MySQL Stack Using Docker Compose | Docker Compose, MySQL, custom network, volumes, Docker Hub push |

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

### Lab 7 — Multi-Network Microservices, Volumes, and Bind Mounts

**Goal:** Deploy a three-tier microservices application using Docker with isolated networks, named volumes, and a bind mount for data persistence.

**What was done:**
- Cloned a Python Flask microservices app with frontend, backend, and notification services
- Wrote Dockerfiles for each service and built their images
- Created two bridge networks with separate subnets to isolate service communication
- Created two named volumes for backend and notification logs
- Created a host directory and configured a bind mount to persist backend message data
- Ran all three containers on their respective networks with volumes attached
- Verified inter-service communication and message creation through the frontend

**Architecture:**
```
[ frontend :3000 ] ── frontend-backend (172.25.0.0/16) ── [ backend :5000 ]
                                                                  |
                                              backend-notification (172.26.0.0/16)
                                                                  |
                                                         [ notification :5001 ]
```

**Key commands:**
```bash
docker build -t frontend-img ./frontend
docker build -t backend-img ./backend
docker build -t notification-img ./notification
docker network create --driver bridge --subnet 172.25.0.0/16 frontend-backend
docker network create --driver bridge --subnet 172.26.0.0/16 backend-notification
docker volume create backend-logs
docker volume create notification-logs
docker run -d --name notification --network backend-notification -v notification-logs:/app/logs notification-img
docker run -d --name backend --network frontend-backend -v backend-logs:/app/logs -v ~/backend-data:/app/data -e NOTIFICATION_URL=http://notification:5001/notify backend-img
docker network connect backend-notification backend
docker run -d --name frontend --network frontend-backend -p 8080:3000 -e BACKEND_URL=http://backend:5000 frontend-img
```

[View Lab 7 README](lab7/README.md)

---

### Lab 8 — Containerized Node.js and MySQL Stack Using Docker Compose

**Goal:** Containerize a Node.js e-commerce application with a MySQL database using Docker Compose, then push the image to Docker Hub.

**What was done:**
- Cloned a Node.js e-commerce application requiring a MySQL connection
- Created a `.env` file for credentials and a `.env.example` with placeholders
- Wrote a `docker-compose.yml` defining the app service, MySQL service, a custom bridge network, and named volumes
- Started the stack and verified the app connected to MySQL and the `ivolve` database was created
- Tested the health endpoint and confirmed the frontend loads in the browser
- Built and tagged the app image and pushed it to Docker Hub

**docker-compose.yml summary:**

| Resource | Configuration |
|----------|--------------|
| App service | Build from Dockerfile, port 3000, env from `.env`, logs volume |
| DB service | mysql:8 image, env from `.env`, db_data volume |
| Network | `ivolve-net` bridge |
| Volumes | `app-logs:/app/logs`, `db_data:/var/lib/mysql` |

**Key commands:**
```bash
docker compose up -d
docker compose logs app
docker compose ps
curl http://localhost:3000/health
docker exec -it ivolveapp-db-1 mysql -u root -prootpassword -e "SHOW DATABASES;"
docker build -t onlyhabiba/ivolve-app:latest .
docker push onlyhabiba/ivolve-app:latest
```

[View Lab 8 README](lab8/README.md)

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
cd lab7/MicroserviceApp
cd lab8/iVolveApp
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
├── lab7/
│   ├── MicroserviceApp/
│   │   ├── frontend/
│   │   ├── backend/
│   │   └── notification/
│   ├── screenshots/
│   └── README.md
├── lab8/
│   ├── iVolveApp/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── .env.example
│   │   ├── server.js
│   │   ├── db.js
│   │   └── frontend/
│   ├── screenshots/
│   └── README.md
└── README.md
```

---

*iVolve Technology — DevOps Training Program*

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
