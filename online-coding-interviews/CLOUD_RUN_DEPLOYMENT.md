# Google Cloud Run Deployment Guide

Complete guide for deploying the Coding Interview Platform to Google Cloud Run. Choose your deployment style below.

---

## 📋 Table of Contents

1. [Quick Deploy (5 minutes)](#quick-deploy)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Troubleshooting](#troubleshooting)
5. [Common Commands](#common-commands)
6. [Monitoring & Management](#monitoring--management)

---

## 🚀 Quick Deploy

**For experienced users or after first setup:**

```bash
PROJECT_ID="your-project-id"
REGION="us-central1"

# 1. Set project
gcloud config set project $PROJECT_ID

# 2. Enable APIs
gcloud services enable containerregistry.googleapis.com run.googleapis.com

# 3. Configure Docker auth
gcloud auth configure-docker gcr.io

# 4. Build image (for Cloud Run: AMD64/Linux)
docker build --platform linux/amd64 -t coding-interview-platform:latest .

# 5. Tag image
docker tag coding-interview-platform:latest \
  gcr.io/$PROJECT_ID/coding-interview-platform:latest

# 6. Push to GCR
docker push gcr.io/$PROJECT_ID/coding-interview-platform:latest

# 7. Deploy to Cloud Run
gcloud run deploy coding-interview-platform \
  --image=gcr.io/$PROJECT_ID/coding-interview-platform:latest \
  --region=$REGION \
  --allow-unauthenticated \
  --platform=managed \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600

# 8. Get URL
gcloud run services describe coding-interview-platform \
  --region=$REGION --format='value(status.url)'
```

**Your app is live!** 🎉

---

## ✅ Prerequisites

Before deploying, ensure you have:

- [ ] **Google Cloud Account** created with billing enabled
- [ ] **gcloud CLI** installed (`gcloud --version`)
- [ ] **Docker** installed and running (`docker ps`)
- [ ] **Project ID** from Google Cloud Console
- [ ] **Authenticated** with gcloud (`gcloud auth application-default login`)
- [ ] **Docker image** built locally (`docker build -t coding-interview-platform .`)

### Check Prerequisites

```bash
# Verify gcloud
gcloud --version

# Verify Docker
docker --version

# List your Google Cloud projects
gcloud projects list

# Check authentication
gcloud auth list
```

---

## 📖 Step-by-Step Setup

### Step 1: Get Your Project ID

If you don't have a project ID yet:

1. Go to https://console.cloud.google.com/
2. Click the project dropdown (top of page)
3. Click "New Project"
4. Name it: `coding-interview-platform`
5. Google will auto-generate a Project ID
6. Click "Create"

**Save your Project ID** - you'll need it for deployment.

### Step 2: Set Up Google Cloud Project

```bash
# Set your project
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# Verify
gcloud config get-value project
```

### Step 3: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build (optional, for advanced builds)
gcloud services enable cloudbuild.googleapis.com
```

### Step 4: Configure Docker Authentication

```bash
# Authenticate Docker with Google Cloud
gcloud auth configure-docker gcr.io

# Verify by pushing a test command
docker push gcr.io/$GCP_PROJECT_ID/test:test 2>&1 | grep -q "unauthorized" && echo "Auth configured"
```

### Step 5: Build Docker Image

**Important:** Cloud Run requires AMD64/Linux architecture. If you're on Mac (ARM64), use the `--platform` flag:

```bash
# Navigate to project directory
cd /Users/zhuye/code/ai-dev-tools-homework/online-coding-interviews

# Build the image for Cloud Run (AMD64/Linux)
docker build --platform linux/amd64 -t coding-interview-platform:latest .

# Verify image was built
docker images | grep coding-interview-platform
```

**Note:** If you get a warning about QEMU, that's normal. Docker will emulate the architecture if needed.

### Step 6: Tag and Push to Google Container Registry

```bash
# Set variables
export GCP_PROJECT_ID="your-project-id"
export IMAGE_NAME="gcr.io/$GCP_PROJECT_ID/coding-interview-platform"

# Tag the image
docker tag coding-interview-platform:latest $IMAGE_NAME:latest

# Push to Google Container Registry
docker push $IMAGE_NAME:latest

# Verify push
gcloud container images list --repository=gcr.io/$GCP_PROJECT_ID
```

### Step 7: Deploy to Cloud Run

```bash
# Set variables
export GCP_PROJECT_ID="your-project-id"
export IMAGE_NAME="gcr.io/$GCP_PROJECT_ID/coding-interview-platform"
export SERVICE_NAME="coding-interview-platform"
export REGION="us-central1"

# Deploy
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 5000 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars FLASK_ENV=production

# Get the service URL
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)'
```

### Step 8: Test Your Deployment

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe coding-interview-platform \
  --region us-central1 --format='value(status.url)')

# Test the service
curl $SERVICE_URL

# View logs
gcloud run services logs read coding-interview-platform \
  --region us-central1 --limit 50
```

**Your application is now live!** 🎉

---

## 🆘 Troubleshooting

### Issue: gcloud command not found

**Solution:**
```bash
# Add to PATH
export PATH="/Users/zhuye/code/ai-dev-tools-homework/online-coding-interviews/google-cloud-sdk-tools/google-cloud-sdk/bin:$PATH"

# Make permanent
echo 'export PATH="/Users/zhuye/code/ai-dev-tools-homework/online-coding-interviews/google-cloud-sdk-tools/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: Docker push fails - "authentication required"

**Solution:**
```bash
# Re-authenticate
gcloud auth configure-docker gcr.io

# Try push again
docker push gcr.io/$GCP_PROJECT_ID/coding-interview-platform:latest
```

### Issue: Cloud Run API not enabled

**Solution:**
```bash
# Enable it
gcloud services enable run.googleapis.com

# Wait 30 seconds, then deploy again
```

### Issue: Service won't start - "Container failed to start"

**Solution:**
```bash
# Check logs
gcloud run services logs read coding-interview-platform \
  --region us-central1 --follow

# Common fixes:
# 1. Ensure port is 5000 (app listens on this)
# 2. Check memory: --memory=512Mi minimum
# 3. Check timeout: --timeout=3600
# 4. Verify environment variables
```

### Issue: "Project not found"

**Solution:**
1. Verify your Project ID: `gcloud projects list`
2. Use exact Project ID (not project name)
3. Ensure you have access to the project

### Issue: WebSocket connection fails

**Solution:**
Cloud Run supports WebSockets by default. If issues occur:
```bash
# Update service with WebSocket support
gcloud run services update coding-interview-platform \
  --region us-central1
```

---

## 📖 Common Commands

### Viewing & Monitoring

```bash
# Get service URL
gcloud run services describe coding-interview-platform \
  --region us-central1 --format='value(status.url)'

# View service details
gcloud run services describe coding-interview-platform \
  --region us-central1

# View logs (recent)
gcloud run services logs read coding-interview-platform \
  --region us-central1 --limit 50

# View logs (live tail)
gcloud run services logs read coding-interview-platform \
  --region us-central1 --follow

# List all deployed services
gcloud run services list

# List container images
gcloud container images list
```

### Configuration Updates

```bash
# Update memory
gcloud run services update coding-interview-platform \
  --memory=512Mi --region us-central1

# Update CPU
gcloud run services update coding-interview-platform \
  --cpu=1 --region us-central1

# Update timeout (in seconds)
gcloud run services update coding-interview-platform \
  --timeout=3600 --region us-central1

# Set environment variables
gcloud run services update coding-interview-platform \
  --update-env-vars=FLASK_ENV=production,LOG_LEVEL=info \
  --region us-central1

# Update min instances (0 = auto-scale to zero)
gcloud run services update coding-interview-platform \
  --min-instances=0 --region us-central1

# Update max instances
gcloud run services update coding-interview-platform \
  --max-instances=50 --region us-central1
```

### Redeployment (after code changes)

```bash
# Build new image
docker build -t coding-interview-platform:latest .

# Tag and push
docker tag coding-interview-platform:latest \
  gcr.io/$GCP_PROJECT_ID/coding-interview-platform:latest
docker push gcr.io/$GCP_PROJECT_ID/coding-interview-platform:latest

# Redeploy
gcloud run deploy coding-interview-platform \
  --image=gcr.io/$GCP_PROJECT_ID/coding-interview-platform:latest \
  --region us-central1
```

### Cleanup & Deletion

```bash
# Delete service
gcloud run services delete coding-interview-platform \
  --region us-central1

# Delete image
gcloud container images delete \
  gcr.io/$GCP_PROJECT_ID/coding-interview-platform

# Delete all images in repository
gcloud container images delete \
  gcr.io/$GCP_PROJECT_ID --recursive

# List what will be deleted
gcloud container images list --repository=gcr.io/$GCP_PROJECT_ID
```

---

## 🔍 Monitoring & Management

### View Metrics

```bash
# Via Cloud Run console
https://console.cloud.google.com/run?project=$GCP_PROJECT_ID

# Via command line
gcloud run services describe coding-interview-platform \
  --region us-central1
```

### Performance Tuning

```bash
# Optimize for speed (high traffic)
gcloud run services update coding-interview-platform \
  --cpu=2 \
  --memory=1Gi \
  --max-instances=100 \
  --min-instances=1 \
  --region us-central1

# Optimize for cost (low traffic)
gcloud run services update coding-interview-platform \
  --cpu=1 \
  --memory=256Mi \
  --max-instances=10 \
  --min-instances=0 \
  --region us-central1

# Recommended for this app
gcloud run services update coding-interview-platform \
  --cpu=1 \
  --memory=512Mi \
  --max-instances=50 \
  --min-instances=0 \
  --region us-central1
```

### Cost Management

**Free Tier Benefits:**
- 2 million requests per month (always free)
- 360,000 vCPU-seconds per month (always free)
- 180,000 GiB-seconds per month (always free)

**Estimated Monthly Costs:**

| Traffic | CPU | Memory | Est. Cost |
|---------|-----|--------|-----------|
| 100 req/day | 0.25 | 128 MB | ~$0 (free tier) |
| 1K req/day | 0.25 | 256 MB | ~$0.50 |
| 10K req/day | 1 | 512 MB | ~$5 |
| 100K req/day | 1 | 512 MB | ~$50 |

**Cost Saving Tips:**
1. Set `--min-instances=0` to scale to zero when idle
2. Use smaller memory if possible (256-512 MB)
3. Monitor logs for inefficient queries
4. Use caching where possible

---

## 🌍 Available Regions

```
us-central1      (Iowa) - Default, cheapest, lowest latency for US
us-east1         (South Carolina)
us-west1         (Oregon)
europe-west1     (Belgium)
asia-northeast1  (Tokyo)
asia-southeast1  (Singapore)
```

**Recommendation:** Use `us-central1` for lowest cost and best US latency.

To change region, replace `us-central1` in commands with your preferred region.

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| **Cloud Run Console** | https://console.cloud.google.com/run |
| **Container Registry** | https://console.cloud.google.com/gcr |
| **Cloud Logs** | https://console.cloud.google.com/logs |
| **Billing** | https://console.cloud.google.com/billing |
| **Cloud Run Docs** | https://cloud.google.com/run/docs |
| **Pricing** | https://cloud.google.com/run/pricing |
| **API Reference** | https://cloud.google.com/run/docs/reference/rest |

---

## 📚 Related Documentation

- **README.md** - Main overview and quick start
- **DOCKER.md** - Docker and local development
- **DEPLOYMENT.md** - General deployment strategies
- **TESTING.md** - Running tests
- **ARCHITECTURE.md** - Technical design and architecture

---

## ✨ Deployment Complete

After following these steps, your application will be live at:
```
https://coding-interview-platform-XXXXX.a.run.app
```

**Next Steps:**
1. Test your live application
2. Share the URL with users
3. Monitor logs and metrics
4. Set up custom domain (optional)
5. Configure auto-scaling as needed

For questions, check the troubleshooting section above or review the related documentation.

Happy deploying! 🚀
