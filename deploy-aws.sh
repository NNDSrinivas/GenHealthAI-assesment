#!/bin/bash

# AWS Deployment Script for GenHealth.AI Clinical Document Processing API
# Production-grade deployment to AWS Elastic Beanstalk

echo "🚀 AWS Production Deployment - GenHealth.AI Clinical Document API"
echo "=================================================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    echo "Install with: pip install awsebcli"
    exit 1
fi

echo "✅ AWS CLI and EB CLI found"
echo ""

# Set deployment variables
APP_NAME="genhealth-clinical-api"
ENV_NAME="genhealth-prod"
REGION="us-east-1"
PLATFORM="python-3.11"

echo "📋 Deployment Configuration:"
echo "   Application: $APP_NAME"
echo "   Environment: $ENV_NAME" 
echo "   Region: $REGION"
echo "   Platform: $PLATFORM"
echo ""

# Initialize Elastic Beanstalk application
echo "🔧 Initializing Elastic Beanstalk application..."
eb init $APP_NAME --platform "$PLATFORM" --region $REGION

# Create environment with load balancer
echo "🌐 Creating production environment..."
eb create $ENV_NAME \
    --instance-types t3.small,t3.medium \
    --min-instances 1 \
    --max-instances 4 \
    --enable-spot \
    --envvars FLASK_ENV=production,FLASK_DEBUG=False,LOG_LEVEL=INFO

# Deploy the application
echo "🚀 Deploying application..."
eb deploy $ENV_NAME

# Get the application URL
URL=$(eb status $ENV_NAME | grep CNAME | awk '{print $2}')

echo ""
echo "🎉 Deployment Complete!"
echo "======================================"
echo "🌐 Application URL: https://$URL"
echo "🔍 Health Check: https://$URL/health"
echo "📚 API Documentation: https://$URL/api"
echo ""
echo "🧪 Test your deployment:"
echo "curl https://$URL/health"
echo ""
echo "📊 Monitor your application:"
echo "eb logs $ENV_NAME --all"
echo "eb health $ENV_NAME"
echo ""
echo "🔧 Useful commands:"
echo "eb open $ENV_NAME    # Open in browser"
echo "eb ssh $ENV_NAME     # SSH to instance"
echo "eb terminate $ENV_NAME  # Terminate when done"
echo ""