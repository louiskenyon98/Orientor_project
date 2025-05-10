#!/bin/bash

# Deployment script for AWS Elastic Beanstalk
# This script builds the Docker image, pushes it to ECR, and deploys to Elastic Beanstalk

# Configuration variables - edit these for your environment
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="826396126555" # Replace with your AWS account ID
ECR_REPOSITORY="navigo-api"
EB_APPLICATION="navigo-api"
EB_ENVIRONMENT="navigo-api-prod"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display welcome message
echo -e "${GREEN}=== Navigo API Deployment to AWS Elastic Beanstalk ===${NC}"
echo "This script will build and deploy the Navigo API to AWS Elastic Beanstalk."

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install it and configure credentials.${NC}"
    exit 1
fi

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker to continue.${NC}"
    exit 1
fi

# Check EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}Warning: EB CLI is not installed. Some deployment steps will be skipped.${NC}"
    EB_CLI_INSTALLED=false
else
    EB_CLI_INSTALLED=true
fi

# Verify AWS credentials
echo -e "${YELLOW}Verifying AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Step 1: Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t $ECR_REPOSITORY:$IMAGE_TAG -f Dockerfile.prod .
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker image built successfully.${NC}"

# Step 2: Authenticate Docker to ECR
echo -e "${YELLOW}Authenticating Docker to ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: ECR authentication failed.${NC}"
    exit 1
fi

# Step 3: Create ECR repository if it doesn't exist
echo -e "${YELLOW}Checking if ECR repository exists...${NC}"
if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create ECR repository.${NC}"
        exit 1
    fi
fi

# Step 4: Tag and push Docker image to ECR
echo -e "${YELLOW}Tagging and pushing Docker image to ECR...${NC}"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to push Docker image to ECR.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker image pushed to ECR successfully.${NC}"

# Step 5: Update Dockerrun.aws.json with correct image URI
echo -e "${YELLOW}Updating Dockerrun.aws.json...${NC}"
sed -i.bak "s|AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com|$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com|g" Dockerrun.aws.json
rm -f Dockerrun.aws.json.bak

# Step 6: Deploy to Elastic Beanstalk
if [ "$EB_CLI_INSTALLED" = true ]; then
    echo -e "${YELLOW}Deploying to Elastic Beanstalk...${NC}"
    
    # Check if EB environment exists
    if ! eb status $EB_ENVIRONMENT &> /dev/null; then
        echo -e "${YELLOW}Creating new Elastic Beanstalk environment...${NC}"
        eb create $EB_ENVIRONMENT \
            --platform "Docker running on 64bit Amazon Linux 2" \
            --instance-type t2.small \
            --min-instances 1 \
            --max-instances 2 \
            --cname $EB_ENVIRONMENT \
            --elb-type application \
            --region $AWS_REGION
    else
        echo -e "${YELLOW}Updating existing Elastic Beanstalk environment...${NC}"
        eb deploy $EB_ENVIRONMENT
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Elastic Beanstalk deployment failed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Deployment to Elastic Beanstalk completed successfully.${NC}"
    
    # Get the application URL
    EB_URL=$(eb status $EB_ENVIRONMENT | grep CNAME | awk '{print $2}')
    echo -e "${GREEN}Application deployed to: http://$EB_URL${NC}"
else
    echo -e "${YELLOW}EB CLI not installed. To deploy to Elastic Beanstalk:${NC}"
    echo "1. Install EB CLI: pip install awsebcli"
    echo "2. Initialize EB environment: eb init -p docker $EB_APPLICATION --region $AWS_REGION"
    echo "3. Create or update environment: eb create/deploy $EB_ENVIRONMENT"
fi

echo -e "${GREEN}Deployment script completed.${NC}"
exit 0 