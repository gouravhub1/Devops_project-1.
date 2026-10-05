pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Code Hygiene & Static Analysis') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install flake8 bandit
                    flake8 --exit-zero app/
                    bandit -r app/ || true
                '''
            }
        }

        stage('Automated Unit & Integration Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    if [ -f app/requirements.txt ]; then
                        pip install -r app/requirements.txt
                    elif [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    pip install pytest psutil
                    export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"
                    pytest --junitxml=test-reports/results.xml || true
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-reports/results.xml'
            sh 'rm -rf venv'
        }
    }
}
