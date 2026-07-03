# Spec: ABC Technologies DevOps Pipeline & Website

## Objective
The objective is to implement a DevOps pipeline that automates the packaging, containerization, orchestration, and continuous monitoring of the "ABC Technologies Corporate Website" (Use Case 1).
Specifically:
1. Create a multi-page static website (Home, About Us, Services, Careers, Contact Us, Gallery) using HTML, CSS, and JS.
2. Package the static website files using Maven into a `.war` file.
3. Build a Docker image based on Nginx that extracts and serves the website files.
4. Deploy the application into local Kubernetes (Docker Desktop) with a Deployment (2 replicas) and a NodePort service on port `30080`.
5. Implement a Jenkins Pipeline (`Jenkinsfile`) to automate: Checkout -> Maven build -> Docker build -> Kubernetes deployment.
6. Configure continuous monitoring:
   - Nagios: Monitor website HTTP health (port `30080`) on the host.
   - Graphite & Grafana: Collect and push system resource metrics (CPU, Memory, Network) and display them on a dashboard.

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS3, Vanilla JS
- **Build Tool**: Apache Maven 3.9+
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Docker Desktop)
- **CI/CD**: Jenkins LTS (listening on `8080`)
- **Monitoring**: Nagios (CGI/Web UI), Graphite (port `8088`), Grafana (port `3000`)
- **Metric Collection**: Python/Bash metrics collector script pushing to Graphite (port `2003`)

## Commands
- **Maven Package**: `mvn clean package`
- **Docker Build**: `docker build -t abc-website:latest .`
- **Docker Run (Local)**: `docker run -d -p 8080:80 --name abc-website abc-website:latest`
- **Kubernetes Deploy**: `kubectl apply -f k8s/`
- **Kubernetes Undeploy**: `kubectl delete -f k8s/`
- **Start Nagios Container**: `docker compose -f monitoring/docker-compose.yml up -d nagios`
- **Start Graphite Container**: `docker compose -f monitoring/docker-compose.yml up -d graphite`
- **Restart Jenkins Brew Service**: `brew services restart jenkins-lts`

## Project Structure
```text
abc-technologies-devops/
├── pom.xml                     # Maven configuration for packaging
├── Dockerfile                  # Multi-stage Docker build using Nginx
├── Jenkinsfile                 # Jenkins declarative CI/CD pipeline
├── website/                    # Static website content
│   ├── index.html              # Home page
│   ├── about.html              # About Us page
│   ├── services.html           # Services page
│   ├── careers.html            # Careers page
│   ├── contact.html            # Contact Us page
│   ├── gallery.html            # Gallery page
│   ├── css/
│   │   └── style.css           # Styling
│   ├── js/
│   │   └── main.js             # Basic interactivity
│   └── images/                 # Image assets (UI and icons)
├── k8s/
│   ├── deployment.yaml         # Kubernetes Deployment configuration
│   └── service.yaml            # NodePort Service (Port 30080)
├── monitoring/
│   ├── docker-compose.yml      # Compose file for Nagios, Graphite, Grafana
│   ├── send_metrics.py         # Script to collect & push resource metrics to Graphite
│   ├── nagios/
│   │   └── abc-website.cfg     # Nagios configuration for HTTP checks
│   └── grafana/
│       └── dashboard.json      # Pre-configured Grafana Dashboard JSON
└── SPEC.md                     # This specification document
```

## Code Style & Conventions
- **HTML5**: Semantic tags, responsive viewport metadata, unique IDs for testing.
- **CSS3**: Variables for layout/colors, flexbox/grid for layouts, media queries for responsiveness.
- **Kubernetes**: Standard naming, explicit resource limits, and correct selector match labels.
- **Jenkinsfile**: Declarative pipeline, environment variables for reuse, proper error handling.

## Testing & Verification Strategy
- **Local Browser Check**: Open `http://localhost:30080` in the browser and verify all pages load and link correctly.
- **CI/CD Build**: Verify the Jenkins build completes successfully and shows green stages.
- **Nagios**: Check status at Nagios UI (should show `HTTP OK` for the port `30080` service).
- **Graphite**: Query `http://localhost:8088/metrics` or verify raw metric paths exist (e.g. `system.cpu`).
- **Grafana**: Open dashboard at `http://localhost:3000` and confirm graph updates with system metrics.

## Boundaries
- **Always do**: Run linting on HTML/CSS if possible, test kubectl commands locally before committing.
- **Ask first**: Changing the NodePort `30080` or Jenkins port `8080`.
- **Never do**: Push secrets, write unversioned scripts, or hardcode environment paths.

## Success Criteria
- [ ] Website is accessible at `http://localhost:30080` and has 6 fully functional pages.
- [ ] Maven successfully packages the website into `target/abc-technologies-devops-1.0.war`.
- [ ] Docker image `abc-website:latest` is built and runs Nginx on port 80.
- [ ] Kubernetes pods are running and NodePort service is active.
- [ ] Jenkins pipeline automates the entire process on git check-in.
- [ ] Nagios container runs and monitors the website status.
- [ ] Metrics collection script pushes CPU/RAM data to Graphite, and Grafana displays it.
- [ ] A ZIP containing all files is packaged for submission.
- [ ] A report is drafted outlining all execution steps.
