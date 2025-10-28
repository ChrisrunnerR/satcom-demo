# 📞 Twilio Voice Integration - Quick Guide

## ✅ **Setup Complete!**

Your FastAPI now has **7 new Twilio voice endpoints** for Ground Station VOIP calls!

---

## 🔑 **Your Twilio Info:**

- **Account SID:** ACxxxxxxxxxxxxxxxxxxxxxxxxxx (stored in .env)
- **Phone Number:** +1 (415) 299-7283
- **Free Trial:** $15 credit (hundreds of test calls!)

---

## 📡 **New Endpoints:**

### **1. Make Outgoing Call**

```bash
POST /api/call/make
```

**Example:**

```json
{
  "to_number": "+14155551234"
}
```

**Use Case:** Ground station initiates call to Air Side

---

### **2. Answer Incoming Call**

```bash
POST /api/call/answer
```

**Automatically called by Twilio** - This is a webhook endpoint

**Use Case:** When Air Side calls Ground station

---

### **3. Send Text to Call (TTS)**

```bash
POST /api/call/send-text
```

**Example:**

```json
{
  "text": "Alpha squad, this is ground control. Message received, over."
}
```

**Use Case:** Send text message that Twilio speaks during active call

---

### **4. Send Audio to Call**

```bash
POST /api/call/send-audio
```

**Example:**

```json
{
  "audio_url": "https://your-server.com/audio/transmission.mp3"
}
```

**Use Case:** Play pre-recorded or generated audio during call

---

### **5. Hang Up Call**

```bash
POST /api/call/hangup
```

**Example:**

```json
{}
```

**Use Case:** End the active call

---

### **6. Get Call Status**

```bash
GET /api/call/status
```

**Returns:**

```json
{
  "call_sid": "CAxxxx",
  "status": "in-progress",
  "duration": "45",
  "from": "+14152997283",
  "to": "+14155551234"
}
```

**Use Case:** Check if call is active, get duration, etc.

---

### **7. Get Call Recordings**

```bash
GET /api/call/recordings/{call_sid}
```

**Returns:**

```json
{
  "recordings": [
    {
      "sid": "RExxxx",
      "url": "https://api.twilio.com/recordings/RExxxx.mp3",
      "duration": "120"
    }
  ]
}
```

**Use Case:** Retrieve recorded audio from completed calls

---

## 🎯 **Test Flow - Air Side → Ground Side:**

### **Scenario 1: Ground Calls Air**

```bash
# 1. Ground initiates call
POST /api/call/make
{"to_number": "+14155551234"}

# 2. Check call status
GET /api/call/status

# 3. Send audio during call
POST /api/call/send-audio
{"audio_url": "https://example.com/audio.mp3"}

# 4. Or send text (TTS)
POST /api/call/send-text
{"text": "This is ground control, over."}

# 5. End call
POST /api/call/hangup
```

### **Scenario 2: Air Calls Ground**

```bash
# 1. Air Side dials: +1-415-299-7283
# 2. Twilio automatically calls: /api/call/answer
# 3. Call is established and recorded
# 4. Ground can send audio/text
# 5. After call ends, get recordings:
GET /api/call/recordings/{call_sid}
```

---

## 🌐 **Configure Twilio Console:**

**Set your webhook URL in Twilio Console:**

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
2. Click on your number: **(415) 299-7283**
3. Under "Voice Configuration":
   - **A Call Comes In:** Webhook
   - **URL:** `https://satcom-project-eqqi5.ondigitalocean.app/api/call/answer`
   - **HTTP:** POST
4. Click **Save**

---

## 🚀 **Next Steps for DigitalOcean:**

### **Add Twilio Env Vars to DigitalOcean:**

1. Go to: https://cloud.digitalocean.com/apps/70878b75-892e-4302-8449-8bea165ce991/settings
2. Click **"App-Level Environment Variables"** → **Edit**
3. Add these:

```
TWILIO_ACCOUNT_SID = ACxxxxxxxxxxxxxxxxxxxxxxxxxx (your Account SID)
TWILIO_AUTH_TOKEN = your_auth_token_here
TWILIO_PHONE_NUMBER = +14152997283
APP_URL = https://satcom-project-eqqi5.ondigitalocean.app
```

4. Save and redeploy!

---

## 🧪 **Test Locally NOW:**

**Open in browser:**

```
http://localhost:8000/docs
```

**You'll see 7 NEW endpoints:**

- POST /api/call/make
- POST /api/call/answer
- POST /api/call/send-audio
- POST /api/call/send-text
- POST /api/call/hangup
- GET /api/call/status
- GET /api/call/recordings/{call_sid}

**Try it:**

1. Click "POST /api/call/make"
2. Click "Try it out"
3. Enter a test number
4. Click "Execute"
5. Make a real call!

---

## 💰 **Cost Reminder:**

- **Free trial:** $15 (enough for 750+ minutes!)
- **After:** ~$1/month + $0.01/minute
- **Perfect for MVP!**

---

## 🎯 **What This Enables:**

✅ **Full bi-directional voice calls**  
✅ **Automatic call recording**  
✅ **Send/receive audio in real-time**  
✅ **Text-to-speech during calls**  
✅ **Call status monitoring**  
✅ **Recording retrieval & analysis**

**Your MVP is now a complete VOIP satcom system!** 🚀
