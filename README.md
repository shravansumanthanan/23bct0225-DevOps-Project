# ABC Technologies DevOps Pipeline & Corporate Website

**Student Name:** Shravan  
**Register Number:** 23BCT0225  
**Course:** DevOps Tools & Practices  

---

## Project Overview
This repository contains the source code, deployment manifests, pipeline configuration, and monitoring setups for the **ABC Technologies Corporate Website**. It demonstrates a complete end-to-end DevOps pipeline executing automation from commit to containerized deployment on a local Kubernetes cluster, coupled with active service and resource monitoring.

---

## Tech Stack & Architecture
- **Web Application:** HTML5, CSS3, JavaScript (Vanilla)
- **Packaging/Build:** Apache Maven 3.9+ (WAR packaging)
- **Containerization:** Docker Engine (Nginx-based multi-stage container)
- **Orchestration:** Kubernetes (Docker Desktop Local Cluster)
- **CI/CD Automation:** Jenkins (Declarative pipeline using `Jenkinsfile`)
- **Uptime Monitoring:** Nagios Core (HTTP check on Port 30080)
- **Performance Monitoring:** Graphite (Metric collection receiver) & Grafana (Visualization panel)
- **System Metrics Daemon:** Python script (`send_metrics.py`) pushing local CPU & Memory stats to Graphite

---

## Directory Structure
```text
abc-technologies-devops/
├── pom.xml                     # Maven project configuration
├── Dockerfile                  # Multi-stage Docker build config
├── Jenkinsfile                 # Jenkins automation pipeline script
├── README.md                   # Setup guide and documentation
├── website/                    # Web application frontend assets
│   ├── index.html              # Home Page
│   ├── about.html              # About Us Page
│   ├── services.html           # Services Page
│   ├── careers.html            # Careers Page
│   ├── contact.html            # Contact Us Page
│   ├── gallery.html            # Gallery Page
│   ├── css/                    # Stylesheets
│   ├── js/                     # Interactivity scripts
│   └── images/                 # Image assets
├── k8s/                        # Kubernetes deployment manifests
│   ├── deployment.yaml         # App Deployment configuration
│   └── service.yaml            # NodePort Service mapping (Port 30080)
└── monitoring/                 # Monitoring configurations
    ├── docker-compose.yml      # Stack setup (Nagios, Graphite, Grafana)
    ├── send_metrics.py         # Python CPU/RAM metric push daemon
    ├── nagios/
    │   └── abc-website.cfg     # Nagios HTTP health check config
    └── grafana/
        └── provisioning/       # Grafana datasource and dashboard auto-configs
```

---

## Installation & Setup Guide

### 1. Build and Package Locally
To clean build the application and compile static resources into a `.war` file:
```bash
mvn clean package
```
This produces `target/abc-technologies-devops-1.0.war`.

### 2. Standalone Docker Container Deployment
To build the Docker image using the multi-stage config:
```bash
docker build -t abc-website:latest .
```
To run the container locally on port `8090`:
```bash
docker run -d -p 8090:80 --name abc-website abc-website:latest
```

### 3. Kubernetes Cluster Deployment
To spin up the service inside the local Kubernetes cluster:
```bash
kubectl apply -f k8s/
```
Verify status:
```bash
kubectl get pods,svc
```

### 4. Run Monitoring Services
Launch Nagios, Graphite, and Grafana using Docker Compose:
```bash
docker compose -f monitoring/docker-compose.yml up -d
```
Start the Python metrics collector daemon to push resource statistics:
```bash
python3 monitoring/send_metrics.py &
```

---

## Accessing Dashboards & Services

| Service | Port / URL | Credentials / Actions |
| :--- | :--- | :--- |
| **Website (Docker)** | `http://localhost:8090` | Standard access |
| **Website (K8s)** | `http://localhost:30080` | Access via Kubernetes NodePort |
| **Jenkins** | `http://localhost:8080` | Local macOS Jenkins instance credentials |
| **Nagios** | `http://localhost:8085` | **User:** `nagiosadmin` \| **Pass:** `nagios` |
| **Graphite** | `http://localhost:8088` | Expand `system` -> `cpu` or `memory` |
| **Grafana** | `http://localhost:3001` | **User:** `admin` \| **Pass:** `admin` *(Dashboard pre-configured)* |
