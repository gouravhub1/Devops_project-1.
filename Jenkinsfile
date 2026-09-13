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
        PROJECT_NAME     = 'devops_project'
        IMAGE_NAME       = "${DOCKER_HUB_USER}/${PROJECT_NAME}"
        BUILD_TAG        = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
    }

    stages {
        stage('Code Hygiene & Static Analysis') {
            steps {
                dir('app') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt

                        echo "[*] Running Bandit Security Linter..."
                        pip install bandit
                        bandit -r . -f txt || true

                        deactivate
                    '''
                }
            }
        }

        stage('Automated Unit & Integration Testing') {
            steps {
                dir('app') {
                    sh '''
                        . .venv/bin/activate
                        export PYTHONPATH=$PYTHONPATH:.
                        pip install pytest pytest-cov
                        mkdir -p test-reports
                        pytest test_app.py -v --junitxml=test-reports/results.xml --cov=. || true
                        deactivate
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'app/test-reports/results.xml'
                }
            }
        }
    }
}
