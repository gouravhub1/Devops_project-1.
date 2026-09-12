pipeline {
    agent any

    options {
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        REGISTRY_CRED_ID = 'dockerhub-credentials'
        DOCKER_HUB_USER  = 'your_dockerhub_username'
        PROJECT_NAME     = 'enterprise-microservice'
        IMAGE_NAME       = "${DOCKER_HUB_USER}/${PROJECT_NAME}"
        BUILD_TAG        = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
    }

    stages {
        stage('Code Hygiene & Static Analysis') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                    
                    echo "[+] Running Bandit Security Linter..."
                    bandit -r app/ -f txt
                    
                    deactivate
                '''
            }
        }

        stage('Automated Unit & Integration Testing') {
            steps {
                sh '''
                    . .venv/bin/activate
                    export PYTHONPATH=$PYTHONPATH:.
                    pytest app/test_app.py -v --junitxml=test-reports/results.xml --cov=app --cov-report=term-missing
                    deactivate
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-reports/results.xml'
                }
            }
        }

        stage('Build Hardened OCI Image') {
            steps {
                sh """
                    docker build --no-cache \
                      -t ${IMAGE_NAME}:${BUILD_TAG} \
                      -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Security Gate: Trivy Image Scan') {
            steps {
                sh """
                    trivy image --severity HIGH,CRITICAL --exit-code 0 ${IMAGE_NAME}:${BUILD_TAG}
                    trivy image --severity CRITICAL --exit-code 1 --ignore-unfixed ${IMAGE_NAME}:${BUILD_TAG}
                """
            }
        }

        stage('Publish Artifacts to Docker Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${REGISTRY_CRED_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${BUILD_TAG}
                        docker push ${IMAGE_NAME}:latest
                        docker logout
                    """
                }
            }
        }

        stage('CD: Ansible Zero-Downtime Deployment') {
            steps {
                sh """
                    ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                      --extra-vars "TARGET_IMAGE=${IMAGE_NAME}:${BUILD_TAG}"
                """
            }
        }
    }

    post {
        always {
            sh '''
                rm -rf .venv
                docker image prune -f || true
            '''
            cleanWs deleteDirs: true, notFailBuild: true
        }
        success {
            echo "Pipeline Run Passed: Deployed Version ${BUILD_TAG}"
        }
        failure {
            echo "Pipeline Failed! Deployment Aborted."
        }
    }
}
