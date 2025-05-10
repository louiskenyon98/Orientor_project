# Navigo API Deployment Guide

This guide explains how to deploy the Navigo API backend to AWS Elastic Beanstalk using Docker.

## Prerequisites

- AWS Account with permissions for:
  - Elastic Beanstalk
  - ECR (Elastic Container Registry)
  - S3
  - IAM
- AWS CLI installed and configured
- Docker installed
- EB CLI installed (optional, but recommended)

## Environment Variables

The following environment variables need to be configured in the AWS Elastic Beanstalk environment:

```
PYTHONPATH=/var/app/venv/staging-.../bin
OPENAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=oasis-embeddings-index
PINECONE_INDEX_NAME_2=recommendation-index
JWT_SECRET_KEY=...
HUGGINGFACE_API_KEY=...
DATABASE_URL=postgresql://...
DB_NAME=navigo

# Custom variables for model access
MODEL_BUCKET=navigo-finetune-embedder-prod
EMBEDDING_S3_PATH=sentence_transformers/
OHE_MODEL_PATH=siamese_models/ohe_Siamese.pkl
PCA_MODEL_PATH=siamese_models/pca384_Siamese.pkl
SCALER_MODEL_PATH=siamese_models/scaler_Siamese.pkl
```

## S3 Model Storage

Models should be stored in S3 with the following structure:

```
navigo-finetune-embedder-prod/
├── sentence_transformers/
│   ├── config.json
│   ├── model.safetensors
│   └── ... (other model files)
└── siamese_models/
    ├── ohe_Siamese.pkl
    ├── pca384_Siamese.pkl
    └── scaler_Siamese.pkl
```

## Deployment Steps

### 1. Preparing for Deployment

1. Ensure all code changes are committed and tested
2. Make sure your AWS credentials are configured: `aws configure`
3. Update the AWS account ID in `scripts/deploy_to_eb.sh`

### 2. Automated Deployment

The easiest way to deploy is using the provided script:

```bash
cd backend
./scripts/deploy_to_eb.sh
```

This script will:
1. Build the Docker image using Dockerfile.prod
2. Push the image to ECR
3. Deploy to Elastic Beanstalk

### 3. Manual Deployment

If you prefer to deploy manually:

1. Build the Docker image:
   ```bash
   docker build -t navigo-api:latest -f Dockerfile.prod .
   ```

2. Tag and push to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   docker tag navigo-api:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/navigo-api:latest
   docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/navigo-api:latest
   ```

3. Update Dockerrun.aws.json with your ECR image URL

4. Create or update EB environment:
   ```bash
   eb init -p docker navigo-api --region us-east-1
   eb create navigo-api-prod
   # Or for existing environment:
   eb deploy navigo-api-prod
   ```

## Monitoring the Deployment

1. Check deployment status:
   ```bash
   eb status navigo-api-prod
   ```

2. View logs:
   ```bash
   eb logs navigo-api-prod
   ```

3. SSH into the instance (if needed):
   ```bash
   eb ssh navigo-api-prod
   ```

## Troubleshooting

- **Model loading issues**: Check `/var/log/eb-hooks.log` for errors
- **Health check failures**: Verify the status of `/health` endpoint
- **Permission problems**: Ensure the EC2 instance has the correct IAM role with S3 access
- **Database connection failures**: Verify the `DATABASE_URL` is correct and security groups allow access

## Important Notes

- Models are dynamically loaded from S3 at runtime - never baked into the Docker image
- The application will show as "initializing" status while models are loading
- `/tmp` directory is used for model storage within the container
- IAM role must have `AmazonS3ReadOnlyAccess` policy attached 