# DigitalOcean Deployment Guide

This guide walks you through deploying the FastAPI backend to DigitalOcean with automatic GitHub Actions deployment.

## 📋 Prerequisites

- GitHub account
- DigitalOcean account (sign up at https://www.digitalocean.com)
- Your API keys (OpenAI, Google Cloud)

## 🚀 Step 1: Create DigitalOcean Droplet

1. **Log into DigitalOcean**: https://cloud.digitalocean.com

2. **Create a new Droplet**:

   - Click "Create" → "Droplets"
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month - 1GB RAM, 1 vCPU)
   - **Datacenter**: Choose closest to you
   - **Authentication**: SSH Key (recommended) or Password
   - **Hostname**: `satcom-demo`
   - Click "Create Droplet"

3. **Wait for droplet creation** (~1 minute)

4. **Note your Droplet IP address** (e.g., 192.168.1.100)

## 🔑 Step 2: Set Up SSH Key (if not done)

### On Mac/Linux:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy your public key
cat ~/.ssh/id_rsa.pub
```

### Add to DigitalOcean:

1. Go to Settings → Security → SSH Keys
2. Click "Add SSH Key"
3. Paste your public key
4. Save

## 🛠️ Step 3: Initial Server Setup

SSH into your droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

Run setup commands:

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create app directory
mkdir -p /home/satcom-demo
cd /home/satcom-demo

# Install Git
apt install git -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/satcom-demo.git .

# Create .env file
nano .env
```

Paste your environment variables:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
GCP_CREDENTIALS='{"type":"service_account","project_id":"satcom-proj",...}'
```

Save and exit (Ctrl+X, Y, Enter)

## 🔐 Step 4: Configure GitHub Secrets

1. Go to your GitHub repo → Settings → Secrets and variables → Actions

2. Add these secrets:

   **DROPLET_IP**

   ```
   YOUR_DROPLET_IP_ADDRESS
   ```

   **DROPLET_USER**

   ```
   root
   ```

   **DROPLET_SSH_KEY**

   ```
   (Paste your PRIVATE SSH key - contents of ~/.ssh/id_rsa)
   ```

## 🎯 Step 5: Deploy!

### Manual First Deploy:

SSH into droplet and run:

```bash
cd /home/satcom-demo
docker-compose up -d --build
```

### Check if it's running:

```bash
docker ps
curl http://localhost:8000/health
```

### Access your API:

```
http://YOUR_DROPLET_IP:8000
```

## 🔄 Step 6: Automatic Deployment

Now whenever you push to `main` branch:

```bash
git add .
git commit -m "Update code"
git push origin main
```

GitHub Actions will automatically:

1. Connect to your droplet
2. Pull latest code
3. Rebuild Docker container
4. Restart the API

## 📊 Step 7: Test Your API

### Health Check:

```bash
curl http://YOUR_DROPLET_IP:8000/health
```

### Generate Text:

```bash
curl -X POST http://YOUR_DROPLET_IP:8000/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{"minutes": 0, "seconds": 10}'
```

### View API Docs:

Open in browser:

```
http://YOUR_DROPLET_IP:8000/docs
```

## 🔒 Step 8: (Optional) Set Up Domain & HTTPS

1. **Buy a domain** (e.g., namecheap.com, godaddy.com)

2. **Point domain to droplet IP**:

   - Add an A record: `@` → `YOUR_DROPLET_IP`
   - Add an A record: `api` → `YOUR_DROPLET_IP`

3. **Install Nginx & SSL**:

```bash
apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
nano /etc/nginx/sites-available/satcom-demo
```

Paste:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com api.YOUR_DOMAIN.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and get SSL:

```bash
ln -s /etc/nginx/sites-available/satcom-demo /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
certbot --nginx -d YOUR_DOMAIN.com -d api.YOUR_DOMAIN.com
```

Now access via HTTPS:

```
https://api.YOUR_DOMAIN.com
```

## 🐛 Troubleshooting

### Check logs:

```bash
docker-compose logs -f
```

### Restart container:

```bash
docker-compose restart
```

### Rebuild from scratch:

```bash
docker-compose down
docker-compose up -d --build
```

### Check if port is open:

```bash
netstat -tulpn | grep 8000
```

## 📝 Useful Commands

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# View running containers
docker ps

# View logs
docker-compose logs -f api

# Restart API
docker-compose restart api

# Update code manually
cd /home/satcom-demo && git pull origin main && docker-compose up -d --build
```

## 💰 Cost Estimate

- **Droplet**: $6/month (Basic plan)
- **Domain** (optional): ~$12/year
- **Total**: ~$6/month for MVP demo

## ✅ You're Done!

Your API is now:

- ✅ Running on DigitalOcean
- ✅ Auto-deploying from GitHub
- ✅ Accessible via HTTP
- ✅ Ready for client demo

Share this URL with your client:

```
http://YOUR_DROPLET_IP:8000/docs
```
