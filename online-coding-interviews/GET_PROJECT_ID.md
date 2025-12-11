# How to Get Your Google Cloud Project ID

## Quick Summary

Your **Project ID** is a unique identifier for your Google Cloud project. You'll need it to deploy your application.

---

## Method 1: Via Google Cloud Console (Easiest) ⭐

### Steps:

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/
   ```

2. **Sign in** with your Google account (if not already signed in)

3. **Find Your Project ID:**
   - Look at the **top of the page** next to the Google Cloud logo
   - You'll see a dropdown showing your project name
   - Click the dropdown to see your **Project ID**
   - It's usually in gray text below the project name

### What It Looks Like:

```
┌─────────────────────────────────┐
│ Google Cloud                    │
│ ▼ My Project (coding-interview-xyz) │
│   Project ID: coding-interview-xyz │
│   Project Number: 123456789012    │
└─────────────────────────────────┘
```

---

## Method 2: Via gcloud CLI (Terminal)

If you prefer using the command line:

### List All Your Projects:
```bash
gcloud projects list
```

### Output Example:
```
PROJECT_ID                NAME                  PROJECT_NUMBER
coding-interview-xyz      My Coding Platform    123456789012
another-project-abc       Another Project       987654321098
```

### Get Your Current Active Project:
```bash
gcloud config get-value project
```

---

## Method 3: Create a New Project (If You Don't Have One)

If you haven't created a project yet:

### Via Console:
1. Go to: https://console.cloud.google.com/
2. Click the **Project dropdown** at the top
3. Click **"New Project"**
4. Enter a name: `coding-interview-platform`
5. Google will auto-generate a Project ID (you can customize it)
6. Click **"Create"**
7. Wait 1-2 minutes for creation
8. Your Project ID will be displayed

### Via gcloud CLI:
```bash
# Create a new project
gcloud projects create coding-interview-platform \
  --name="My Coding Interview Platform"

# The output will show your Project ID
```

---

## Project ID vs Project Name

| Aspect | Project ID | Project Name |
|--------|-----------|-------------|
| **Purpose** | Machine identifier (used in commands) | Human-readable label |
| **Format** | Lowercase, numbers, hyphens | Any text |
| **Example ID** | `coding-interview-xyz` | `My Coding Platform` |
| **Changeable** | ❌ No (permanent) | ✅ Yes |
| **Where Used** | Terminal, API, image registry | Cloud Console UI |

---

## Common Project ID Formats

Google Cloud auto-generates Project IDs like:

- `my-project-12345`
- `coding-platform-abc123`
- `interview-tool-xyz789`

Your project ID will be **unique** across all of Google Cloud.

---

## Next Steps

### Once You Have Your Project ID:

1. **Enable Billing** (required for Cloud Run):
   - Go to: https://console.cloud.google.com/billing
   - Link a billing account to your project
   - This is free if you stay under the free tier limits

2. **Deploy Your Application**:
   ```bash
   cd /Users/zhuye/code/ai-dev-tools-homework/online-coding-interviews

   ./deploy-to-cloud-run.sh YOUR-PROJECT-ID us-central1
   ```

   Example:
   ```bash
   ./deploy-to-cloud-run.sh coding-interview-xyz us-central1
   ```

3. **Wait for Deployment** (5-10 minutes)

4. **Access Your Live App**:
   - URL will be shown after deployment
   - Format: `https://coding-interview-platform-xxxxx.a.run.app`

---

## Troubleshooting

### Problem: Can't find Project ID in Console

**Solution:**
1. Make sure you're signed into your Google account
2. Refresh the page (Cmd+R or Ctrl+R)
3. Check if you have created a project yet
4. If not, click "Create Project" button

### Problem: gcloud shows "No projects found"

**Solution:**
```bash
# Set account first
gcloud auth list

# Select your account
gcloud config set account YOUR-EMAIL@gmail.com

# Now list projects
gcloud projects list
```

### Problem: Need to Create First Project

**Solution:**
1. Go to: https://console.cloud.google.com/
2. Click **"Select a Project"** dropdown
3. Click **"New Project"**
4. Fill in project name
5. Wait for creation
6. Your new Project ID will appear in the dropdown

---

## Quick Reference

**Command to use your Project ID for deployment:**

```bash
# Replace YOUR-PROJECT-ID with your actual ID
./deploy-to-cloud-run.sh YOUR-PROJECT-ID us-central1

# Real example:
./deploy-to-cloud-run.sh my-project-12345 us-central1
```

---

## Links

| Resource | URL |
|----------|-----|
| **Cloud Console** | https://console.cloud.google.com/ |
| **Create Project** | https://console.cloud.google.com/projectcreate |
| **Billing** | https://console.cloud.google.com/billing |
| **Cloud Run** | https://console.cloud.google.com/run |
| **Docs** | https://cloud.google.com/docs/overview |

---

## Need Help?

If you're still having trouble:

1. **Check**: Are you signed into Google Cloud Console?
2. **Check**: Do you have a Google Cloud account (with billing enabled)?
3. **Check**: Does your project exist in the dropdown?

For complete deployment guide, see: `DEPLOYMENT_STATUS.md`
