#!/bin/bash

# AWS App Runner Deployment Script (Serverless option)
# Simpler deployment with automatic scaling

echo "🏃‍♂️ AWS App Runner Deployment - GenHealth.AI Clinical Document API"
echo "=================================================================="
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ Please install AWS CLI first"
    exit 1
fi

# Set variables
SERVICE_NAME="genhealth-clinical-api"
REPO_URL="https://github.com/YOUR_USERNAME/genhealth-clinical-api"
REGION="us-east-1"

echo "📋 App Runner Configuration:"
echo "   Service: $SERVICE_NAME"
echo "   Repository: $REPO_URL"
echo "   Region: $REGION"
echo ""

# Create App Runner service
echo "🚀 Creating App Runner service..."

# Create service configuration
cat > apprunner-service.json << EOF
{
  "ServiceName": "$SERVICE_NAME",
  "SourceConfiguration": {
    "AutoDeploymentsEnabled": true,
    "CodeRepository": {
      "RepositoryUrl": "$REPO_URL",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "CONFIGURATION_FILE",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "gunicorn --bind 0.0.0.0:8000 application:application",
          "RuntimeEnvironmentVariables": {
            "FLASK_ENV": "production",
            "FLASK_DEBUG": "False"
          }
        }
      }
    }
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 20,
    "Timeout": 5,
    "HealthyThreshold": 2,
    "UnhealthyThreshold": 5
  }
}
EOF

# Deploy to App Runner
aws apprunner create-service \
    --cli-input-json file://apprunner-service.json \
    --region $REGION

echo ""
echo "🎉 App Runner service created!"
echo "📊 Check status with:"
echo "aws apprunner list-services --region $REGION"
echo ""

# Clean up
rm apprunner-service.json