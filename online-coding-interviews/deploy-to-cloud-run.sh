#!/bin/zsh

# Google Cloud Run Deployment Script
# Usage: ./deploy-to-cloud-run.sh <project-id> [region]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate inputs
if [ -z "$1" ]; then
    echo -e "${RED}Error: Google Cloud Project ID is required${NC}"
    echo "Usage: $0 <project-id> [region]"
    echo ""
    echo "Example: $0 my-project us-central1"
    exit 1
fi

GCP_PROJECT_ID="$1"
REGION="${2:-us-central1}"
SERVICE_NAME="coding-interview-platform"
IMAGE_NAME="gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Google Cloud Run Deployment Script                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: $GCP_PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Set project
echo -e "${YELLOW}[1/6]${NC} Setting Google Cloud project..."
gcloud config set project $GCP_PROJECT_ID
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Project set successfully"
else
    echo -e "${RED}✗${NC} Failed to set project"
    exit 1
fi
echo ""

# Step 2: Enable APIs
echo -e "${YELLOW}[2/6]${NC} Enabling required Google Cloud APIs..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} APIs enabled"
else
    echo -e "${RED}✗${NC} Failed to enable APIs"
    exit 1
fi
echo ""

# Step 3: Configure Docker
echo -e "${YELLOW}[3/6]${NC} Configuring Docker authentication..."
gcloud auth configure-docker gcr.io --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Docker authenticated"
else
    echo -e "${RED}✗${NC} Failed to configure Docker"
    exit 1
fi
echo ""

# Step 4: Build and push image
echo -e "${YELLOW}[4/6]${NC} Building Docker image..."
docker build -t $IMAGE_NAME:latest .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Docker image built successfully"
else
    echo -e "${RED}✗${NC} Failed to build Docker image"
    exit 1
fi
echo ""

echo -e "${YELLOW}[5/6]${NC} Pushing image to Google Container Registry..."
docker push $IMAGE_NAME:latest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Image pushed successfully"
else
    echo -e "${RED}✗${NC} Failed to push image"
    exit 1
fi
echo ""

# Step 5: Deploy to Cloud Run
echo -e "${YELLOW}[6/6]${NC} Deploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 5000 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars LOG_LEVEL=info \
  --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Deployment successful"
else
    echo -e "${RED}✗${NC} Deployment failed"
    exit 1
fi
echo ""

# Get service URL
echo -e "${YELLOW}Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Service Details:${NC}"
echo "  Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Project: $GCP_PROJECT_ID"
echo ""
echo -e "${YELLOW}Access Your Application:${NC}"
echo -e "${GREEN}${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:     gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit 50"
echo "  View status:   gcloud run services describe $SERVICE_NAME --region $REGION"
echo "  Update code:   $0 $GCP_PROJECT_ID $REGION  (run this again after code changes)"
echo ""
