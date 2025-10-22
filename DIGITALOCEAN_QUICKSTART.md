# DigitalOcean Quick Start Guide

## 🚀 Super Simple 15-Minute Setup

### Step 1: Create DigitalOcean Account (2 min)

1. Go to: https://www.digitalocean.com
2. Click "Sign Up" 
3. Use your email or GitHub account
4. Add a payment method (they give you $200 free credit for 60 days!)

### Step 2: Create Your First Droplet (5 min)

1. **Click "Create" → "Droplets"**

2. **Choose Configuration:**
   - **Region**: Pick closest to you (e.g., San Francisco, New York)
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: 
     - Click "Basic" plan
     - Choose **$6/month** (1GB RAM, 1 vCPU, 25GB SSD)
   
3. **Authentication**:
   - **Option A (Recommended)**: SSH Key
     - Run this on your Mac: `cat ~/.ssh/id_rsa.pub`
     - Copy the output
     - Click "New SSH Key"
     - Paste your key
     - Name it "My Mac"
   - **Option B**: Password (simpler but less secure)
   
4. **Hostname**: `satcom-api`

5. **Click "Create Droplet"** (wait ~1 minute)

6. **Copy your droplet IP address** (e.g., 192.168.1.100)

### Step 3: Connect to Your Droplet (1 min)

```bash
ssh root@YOUR_DROPLET_IP
```

Type "yes" when asked about fingerprint.

### Step 4: Install Docker & Setup (5 min)

Copy and paste these commands one at a time:

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Git
apt install git -y

# Clone your repo
git clone https://github.com/ChrisrunnerR/satcom-demo.git /home/satcom-demo

# Go to app directory
cd /home/satcom-demo

# Create environment file
nano .env
```

### Step 5: Add Your API Keys (2 min)

Paste this into the nano editor (use your actual keys):

```bash
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
GCP_CREDENTIALS={"type":"service_account","project_id":"satcom-proj",...}
```

Press:
- `Ctrl+X`
- `Y` 
- `Enter`

### Step 6: Start Your API! (1 min)

```bash
docker-compose up -d --build
```

Wait 2-3 minutes for it to build and start.

### Step 7: Test It! (1 min)

```bash
curl http://localhost:8000/health
```

You should see: `{"status":"healthy"}`

### Step 8: Access From Anywhere

Your API is now live at:
```
http://YOUR_DROPLET_IP:8000
```

**Interactive Docs:**
```
http://YOUR_DROPLET_IP:8000/docs
```

Share this URL with your client!

---

## 🔄 Automatic Deployment Setup (Optional - 10 min)

### Set Up GitHub Actions for Auto-Deploy:

1. **In Your GitHub Repo** → Settings → Secrets and variables → Actions

2. **Add 3 Secrets:**

   **Name:** `DROPLET_IP`
   **Value:** Your droplet IP (e.g., 192.168.1.100)

   **Name:** `DROPLET_USER`
   **Value:** `root`

   **Name:** `DROPLET_SSH_KEY`
   **Value:** Your private SSH key
   ```bash
   # Get your private key:
   cat ~/.ssh/id_rsa
   ```
   Copy the ENTIRE output including `-----BEGIN` and `-----END` lines

3. **Test Auto-Deploy:**

   Make any change to your code, then:
   ```bash
   git add .
   git commit -m "Test auto-deploy"
   git push origin main
   ```

   GitHub will automatically deploy to your droplet!

---

## 🐛 Troubleshooting

### Check if server is running:
```bash
ssh root@YOUR_DROPLET_IP
cd /home/satcom-demo
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f
```

### Restart server:
```bash
docker-compose restart
```

### Rebuild from scratch:
```bash
docker-compose down
docker-compose up -d --build
```

### Check firewall:
```bash
ufw status
# If active and blocking port 8000:
ufw allow 8000
```

---

## 💰 Costs

- **Droplet**: $6/month
- **Free $200 credit**: Covers 33 months!
- **Cancel anytime**: No contracts

---

## ✅ You're Done!

Your API is:
- ✅ Running on DigitalOcean
- ✅ Accessible from anywhere
- ✅ Auto-deploying from GitHub (if you set it up)
- ✅ Ready for client demo

**Share this with your client:**
```
http://YOUR_DROPLET_IP:8000/docs
```

They can test all the endpoints right in their browser!

---

## 🎯 Next Steps

1. **Buy a domain** (optional): namecheap.com (~$10/year)
2. **Set up HTTPS** (optional): Use Certbot for free SSL
3. **Add authentication** (optional): Protect your API
4. **Monitor usage** (optional): Set up logging

For now, you have a working demo API! 🚀

