#!/bin/bash

# Aira Lambda Deployment Script
# This script packages and deploys both Lambda functions

set -e

echo "🚀 Starting Aira Lambda Deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using environment variables."
fi

# Check required environment variables
required_vars=("AWS_REGION" "BUCKET_IN" "BUCKET_OUT" "GEMINI_API_KEY" "META_ACCESS_TOKEN" "META_PHONE_ID" "META_VERIFY_TOKEN" "DYNAMODB_TABLE")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        exit 1
    fi
done

# Package Lambda Ingestor
echo "📦 Packaging Lambda Ingestor..."
zip -j lambda_ingestor.zip lambda_ingestor.py

# Package Lambda Responder
echo "📦 Packaging Lambda Responder..."
zip -j lambda_responder.zip lambda_responder.py

# Deploy Lambda Ingestor
echo "🚀 Deploying Lambda Ingestor..."
aws lambda update-function-code \
    --function-name aira-ingestor \
    --zip-file fileb://lambda_ingestor.zip \
    --region $AWS_REGION

# Update environment variables for Ingestor
aws lambda update-function-configuration \
    --function-name aira-ingestor \
    --environment "Variables={AWS_REGION=$AWS_REGION,BUCKET_IN=$BUCKET_IN,BUCKET_OUT=$BUCKET_OUT,GEMINI_API_KEY=$GEMINI_API_KEY,META_ACCESS_TOKEN=$META_ACCESS_TOKEN,META_PHONE_ID=$META_PHONE_ID,META_VERIFY_TOKEN=$META_VERIFY_TOKEN,DYNAMODB_TABLE=$DYNAMODB_TABLE}" \
    --region $AWS_REGION

# Deploy Lambda Responder
echo "🚀 Deploying Lambda Responder..."
aws lambda update-function-code \
    --function-name aira-responder \
    --zip-file fileb://lambda_responder.zip \
    --region $AWS_REGION

# Update environment variables for Responder
aws lambda update-function-configuration \
    --function-name aira-responder \
    --environment "Variables={AWS_REGION=$AWS_REGION,BUCKET_OUT=$BUCKET_OUT,GEMINI_API_KEY=$GEMINI_API_KEY,META_ACCESS_TOKEN=$META_ACCESS_TOKEN,META_PHONE_ID=$META_PHONE_ID,DYNAMODB_TABLE=$DYNAMODB_TABLE}" \
    --region $AWS_REGION

# Clean up
echo "🧹 Cleaning up..."
rm lambda_ingestor.zip lambda_responder.zip

echo "✅ Deployment complete!"
