pipeline {
    agent any

    environment {
        // Ensure Homebrew and Docker commands are available in the PATH
        PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls latest source code automatically when using Git SCM
                checkout scm
            }
        }

        stage('Maven Build') {
            steps {
                echo 'Packaging static website files into WAR...'
                sh 'mvn clean package'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker container using Nginx...'
                sh 'docker build -t abc-website:latest .'
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                echo 'Orchestrating container in Kubernetes cluster...'
                sh 'kubectl apply -f k8s/'
                sh 'kubectl rollout status deployment/abc-website'
            }
        }
    }
}
