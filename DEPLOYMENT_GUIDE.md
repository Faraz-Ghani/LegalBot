# Streamlit Cloud Deployment Guide

## Pre-Deployment Checklist ✓

Before deploying to Streamlit Cloud, ensure all of these are complete:

### Repository Setup
- [ ] Repository is public on GitHub
- [ ] All code files committed: `app.py`, `chat.py`, `retrieve.py`, `ingest.py`, `test_suite.py`
- [ ] Dependencies pinned in `requirements.txt`
- [ ] `.env` file is in `.gitignore` (NOT committed)
- [ ] `.streamlit/secrets.toml` is in `.gitignore` (NOT committed)
- [ ] `README.md` created with deployment instructions
- [ ] `.streamlit/config.toml` configured for production

### Code Quality
- [ ] All imports work correctly
- [ ] No hardcoded API keys in code
- [ ] Test suite passes: `python3 test_suite.py`
- [ ] App runs locally: `streamlit run app.py`
- [ ] No debug print statements in production code

### Documentation
- [ ] README.md explains deployment steps
- [ ] TESTING_GUIDE.md documents testing procedures
- [ ] TEST_PROCEDURE.md explains test suite
- [ ] Code comments explain complex logic
- [ ] `.streamlit/secrets.example.toml` shows required secrets

### Data Files
- [ ] Legal documents ready (PDFs in `./Data/` or external storage)
- [ ] PDFs are UTF-8 encoded
- [ ] Total size under 2GB (Streamlit Cloud limit)
- [ ] File permissions allow reading

### API Keys
- [ ] Groq API key obtained from https://console.groq.com/keys
- [ ] No API keys committed to GitHub

---

## Step-by-Step Deployment

### 1. Verify GitHub Repository

```bash
# Ensure all changes committed
git status

# Should show: "On branch main, nothing to commit"

# Verify remote is set correctly
git remote -v

# Should show your GitHub URL
# origin  https://github.com/YOUR_USERNAME/LegalBot.git
```

### 2. Deploy on Streamlit Cloud

**Option A: Deploy via Streamlit UI**

1. Go to https://share.streamlit.io
2. Click **"New app"** button (top-right)
3. Fill in deployment form:
   - **GitHub repository**: `YOUR_USERNAME/LegalBot`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **"Deploy"**

**Option B: Deploy via CLI**

```bash
# Login to Streamlit Cloud
streamlit login

# Deploy directly from repository
streamlit deploy \
  --url https://github.com/YOUR_USERNAME/LegalBot \
  --branch main \
  --file app.py
```

### 3. Set Environment Secrets

**Via Streamlit Cloud Dashboard:**

1. Navigate to your deployed app
2. Click **≡ Settings** (top-right) → **Secrets**
3. In the **Secrets** editor, add:

```toml
# Required: Groq API Key
GROQ_API_KEY = "gsk_YOUR_ACTUAL_KEY_HERE"
```

4. Click **Save**

**Important**: Secrets are stored securely and are NOT visible in the repository.

### 4. Configure App Settings

**For better performance, in Settings panel:**

- **Run on Save**: ON
- **Memory**: Keep auto-selected
- **Timeout**: 900 seconds (15 minutes)
- **Theme**: Light (or match in `config.toml`)

### 5. Add Legal Documents

**Option A: Upload via App UI**
- Use "Upload PDF Documents" in sidebar
- Files stored in session state (resets on redeploy)

**Option B: Store in GitHub (if <100MB total)**
```bash
# Add PDF files to Data directory
git add Data/*.pdf
git commit -m "Add legal documents"
git push
```

**Option C: Use External Storage (Recommended)**

For files >100MB, use cloud storage:

**Google Drive Example:**
```python
# In ingest.py, add:
from google.colab import drive
drive.mount('/content/drive')
pdf_path = '/content/drive/My Drive/Data/'
```

**AWS S3 Example:**
```python
import boto3
s3 = boto3.client('s3')
s3.download_file('bucket-name', 'file.pdf', 'local_path')
```

**Add credentials as Streamlit Secrets:**
```toml
AWS_ACCESS_KEY_ID = "your_key"
AWS_SECRET_ACCESS_KEY = "your_secret"
AWS_S3_BUCKET = "your_bucket"
```

### 6. Monitor Deployment

**Check Deployment Status:**
- Green indicator = Running ✅
- Yellow indicator = Starting
- Red indicator = Error ❌

**View Logs:**
1. Click app → **Logs** tab
2. Look for any error messages
3. Check for missing dependencies

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| "Module not found" | Add missing package to `requirements.txt` |
| "GROQ_API_KEY not found" | Verify secret is set in Settings → Secrets |
| "No documents found" | Check if PDFs are in `./Data/` or using external storage |
| "Out of memory" | Reduce `k` value in retrieve.py or split documents |
| "Timeout" | Increase timeout in Settings or optimize query processing |

---

## Post-Deployment Verification

### 1. Test Basic Functionality

```bash
# Access your deployed app
https://YOUR_APP_NAME.streamlit.app

# Test these queries:
1. "What is section 302?"
2. "What are the punishments for qatl-i-amd?"
3. "Define offence under PPC"
4. "What is qisas?"
5. "Explain ta'zir in Islamic law"
```

### 2. Monitor Performance

**In Streamlit Cloud Dashboard:**
- Check Memory usage (should stay <500MB)
- Check CPU usage (spikes are normal)
- Monitor error rate (should be 0%)

**Expected Metrics:**
```
First query: 1-2 seconds (loading documents)
Subsequent queries: 0.2-0.5 seconds
Memory usage: 200-400MB
```

### 3. Verify All Features

- [ ] Chat history works
- [ ] PDF upload works (if enabled)
- [ ] Query expansion works (try section numbers)
- [ ] Source citations appear
- [ ] Streaming responses work
- [ ] Mobile UI is responsive

---

## Updating Your App

### Make Code Changes

```bash
# Make changes to app.py, retrieve.py, etc.
git add .
git commit -m "Your descriptive message"
git push
```

**Streamlit Cloud automatically redeploys** when you push to main branch (~30-60 seconds).

### Update Dependencies

```bash
# Update requirements.txt
pip install --upgrade package-name
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Update Legal Documents

**If storing in GitHub:**
```bash
git add Data/new_document.pdf
git commit -m "Add new legal document"
git push
```

**If using external storage:**
1. Upload to S3/Google Drive
2. No GitHub action needed
3. Changes take effect immediately

---

## Scaling Considerations

### Current Limitations
- Streamlit Cloud free tier: 1GB RAM, 3GB storage
- Max file upload: 200MB
- Session timeout: 2 hours
- Concurrent users: 1 (free tier)

### For Production/Scaling

**Option 1: Upgrade Streamlit Cloud**
- Streamlit Cloud Teams: Multiple concurrent users, dedicated resources
- Cost: $20-100+/month

**Option 2: Self-Hosted on Cloud Provider**

**AWS EC2:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py --server.port 8501
```

**Google Cloud Run:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port", "8080"]
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group mygroup \
  --name legalbot \
  --image legalbot:latest \
  --port 8501
```

---

## Security Best Practices

### API Keys
- ✅ Store in Streamlit Secrets (never in `.env` on production)
- ✅ Rotate keys every 90 days
- ✅ Monitor usage for unusual activity
- ❌ Never commit to GitHub
- ❌ Never log API keys

### Data Security
- ✅ Use HTTPS only (Streamlit Cloud provides this)
- ✅ Encrypt sensitive data at rest
- ✅ Implement access controls for sensitive documents
- ✅ Regular security audits
- ❌ No PII in logs

### Code Security
- ✅ Keep dependencies updated: `pip install --upgrade`
- ✅ Run security checks: `pip-audit`
- ✅ Regular code reviews
- ✅ Use `.gitignore` properly
- ❌ No hardcoded credentials

### Monitoring
```bash
# Check for security vulnerabilities
pip install pip-audit
pip-audit

# Check for outdated packages
pip list --outdated

# Update secure packages
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting Deployment

### App Won't Start
```
Error: "Failed to import streamlit"
Solution: Check requirements.txt, reinstall dependencies
```

```
Error: "ModuleNotFoundError: No module named 'groq'"
Solution: Add missing package to requirements.txt, re-push
```

### Slow Performance
```
Problem: Queries taking >5 seconds
Solution: 
- Check k value (reduce from 20 to 10)
- Check document size (split large PDFs)
- Check Streamlit Cloud memory usage
```

### API Key Issues
```
Error: "GROQ_API_KEY not found"
Solution:
1. Check secret name matches exactly (case-sensitive)
2. Verify key is valid on console.groq.com
3. Restart app after adding secret
```

### Document Loading Issues
```
Error: "No documents found in Data directory"
Solution:
- Verify PDFs are in ./Data/ or external storage
- Check file permissions
- Ensure PDFs are not corrupted
- Try uploading via app sidebar
```

---

## Rollback to Previous Version

If deployment causes issues:

```bash
# View commit history
git log --oneline

# Revert to previous version
git revert <commit-hash>
git push

# Streamlit Cloud automatically redeploys
```

---

## Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Cloud Help**: https://share.streamlit.io/help
- **LangChain Docs**: https://docs.langchain.com
- **Groq API Docs**: https://console.groq.com/docs
- **GitHub Issues**: https://github.com/Faraz-Ghani/LegalBot/issues

---

## Deployment Checklist (Final)

Before considering deployment complete:

- [ ] App loads without errors
- [ ] All 5 test queries return results
- [ ] Response time is acceptable (<2 seconds)
- [ ] Mobile UI is responsive
- [ ] Secrets are properly set
- [ ] Documents are accessible
- [ ] No error logs visible
- [ ] All features working (chat, upload, etc.)

---

**Status**: ✅ Ready to Deploy  
**Last Updated**: March 19, 2026
