# 🛠️ Development Workflow Guide

## 🎯 Quick Reference

### **Your URLs:**

**Local Development:**

- FastAPI: http://localhost:8000/docs
- Streamlit: http://localhost:8501

**Live Production:**

- FastAPI: https://satcom-project-eqqi5.ondigitalocean.app
- Docs: https://satcom-project-eqqi5.ondigitalocean.app/docs

---

## 🔄 **Development Workflow:**

### **1. Start Working on New Feature**

```bash
cd /Users/admin/Desktop/satcom-demo
git checkout christopher
git pull origin christopher
source venv/bin/activate
```

### **2. Run Local Development Server**

**For FastAPI (REST API):**

```bash
python main.py
```

Open: http://localhost:8000/docs

**For Streamlit (UI):**

```bash
streamlit run streamlit_app.py
```

Open: http://localhost:8501

### **3. Make Your Changes**

- Edit files in your code editor
- Test locally at http://localhost:8000/docs
- Fix any issues

### **4. Commit to Christopher Branch**

```bash
git add .
git commit -m "Describe what you changed"
git push origin christopher
```

### **5. When Ready for Production - Deploy!**

```bash
# Switch to main
git checkout main

# Merge your changes
git merge christopher

# Push to production (auto-deploys!)
git push origin main
```

**Wait 3-5 minutes** → Your changes are LIVE at:
https://satcom-project-eqqi5.ondigitalocean.app/docs

---

## 🎮 **Quick Commands:**

### **Start Local FastAPI:**

```bash
cd /Users/admin/Desktop/satcom-demo
source venv/bin/activate
python main.py
```

### **Stop Local Server:**

Press `Ctrl+C` in the terminal

### **Check What's Running:**

```bash
# Check if local API is running:
curl http://localhost:8000/health

# Check if live API is running:
curl https://satcom-project-eqqi5.ondigitalocean.app/health
```

### **Kill Process on Port 8000 (if stuck):**

```bash
lsof -ti:8000 | xargs kill -9
```

---

## 📂 **Branch Strategy:**

| Branch          | Purpose                           | Where It Runs       |
| --------------- | --------------------------------- | ------------------- |
| **christopher** | Development, testing new features | Your Mac (local)    |
| **main**        | Production, stable code           | DigitalOcean (live) |

**Golden Rule:**

- ✅ **Experiment on christopher**
- ✅ **Deploy from main**

---

## 🐛 **Troubleshooting:**

### **"Address already in use" error:**

```bash
# Kill whatever is on port 8000:
lsof -ti:8000 | xargs kill -9

# Then restart:
python main.py
```

### **"Module not found" error:**

```bash
# Make sure venv is activated:
source venv/bin/activate

# Reinstall dependencies:
pip install -r requirements.txt
```

### **Check deployment status:**

Go to: https://cloud.digitalocean.com/apps

---

## 🎯 **Two Endpoints Explained:**

### **`/` (Root) - API Info**

**What it is:**

- Quick status check
- Shows all available endpoints
- Like a "Hello, I'm alive!" message

**When to use:**

- Check if API is up
- See what endpoints exist
- Monitoring/health checks

**Example:**

```bash
curl https://satcom-project-eqqi5.ondigitalocean.app/
```

**Returns:**

```json
{
  "message": "Satcom Audio Transmission API",
  "status": "running",
  "endpoints": {...}
}
```

### **`/docs` - Interactive Testing**

**What it is:**

- Beautiful UI to test all endpoints
- Fill in parameters with forms
- Execute requests with buttons
- See responses immediately

**When to use:**

- Testing your API
- Demoing to clients
- Learning how it works
- Quick debugging

**Just open in browser:**
https://satcom-project-eqqi5.ondigitalocean.app/docs

---

## 💡 **Think of it Like This:**

**`/` (root)** = Front desk receptionist

- "Hello! We're open!"
- "Here's a directory of services"
- Quick info only

**`/docs`** = Full showroom with demos

- "Try everything!"
- Interactive buttons
- See it work in real-time

Both are useful, just different purposes!

---

## ✅ **You're Ready to Develop!**

**Current Setup:**

- ✅ On christopher branch
- ✅ Local API running at http://localhost:8000
- ✅ Can test at http://localhost:8000/docs
- ✅ Ready to add features!

**When you make changes:**

1. Edit code
2. Restart `python main.py` to see changes
3. Test at http://localhost:8000/docs
4. Commit when it works
5. Merge to main when ready to deploy

---

## 🚀 **Start Developing:**

**Open these NOW:**

1. **Code Editor:** Make changes to `main.py`
2. **Browser:** http://localhost:8000/docs (test your changes)
3. **Terminal:** See logs from `python main.py`

**You're all set!** What feature do you want to add first? 🎉
