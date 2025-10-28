# 🚀 QUICK TEST GUIDE - Satcom MVP Demo

## 📞 **Your Twilio Numbers**

| Number              | Purpose              | Role                                    |
| ------------------- | -------------------- | --------------------------------------- |
| **+1-415-299-7283** | Ground Control       | Makes outgoing calls, receives incoming |
| **+1-978-838-4309** | Air Side (Satellite) | Receives test calls                     |

---

## ✅ **5-MINUTE QUICK TEST**

### **TEST 1: Make Outgoing Call** (1 minute)

```bash
curl -X POST https://satcom-project-eqqi5.ondigitalocean.app/api/call/make \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+19788384309"}'
```

**Expected:**

- ✅ Call to +1-978-838-4309 rings immediately
- ✅ Returns Call SID like `CA17e4ba4400a0df3dc14888fa9b007896`

---

### **TEST 2: Send Text-to-Speech** (30 seconds)

**First, save the Call SID from Test 1, then:**

```bash
curl -X POST https://satcom-project-eqqi5.ondigitalocean.app/api/call/send-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ground Control to Satellite. Mission status nominal. Over."
  }'
```

**Expected:**

- ✅ Hears voice saying the message during active call
- ✅ Clear audio quality

---

### **TEST 3: Hang Up Call** (10 seconds)

```bash
curl -X POST https://satcom-project-eqqi5.ondigitalocean.app/api/call/hangup
```

**Expected:**

- ✅ Call ends immediately
- ✅ Clean disconnect

---

### **TEST 4: Get Call Status** (10 seconds)

```bash
curl "https://satcom-project-eqqi5.ondigitalocean.app/api/call/status?call_sid=YOUR_CALL_SID_HERE"
```

**Expected:**

```json
{
  "status": "completed",
  "duration": "11",
  "start_time": "2025-10-28 01:58:31+00:00"
}
```

---

### **TEST 5: Get Recording** (30 seconds)

```bash
curl "https://satcom-project-eqqi5.ondigitalocean.app/api/call/recordings/YOUR_CALL_SID_HERE"
```

**Expected:**

```json
{
  "recordings": [
    {
      "url": "https://api.twilio.com/.../recording.mp3",
      "duration": "9"
    }
  ]
}
```

---

### **TEST 6: Incoming Call** (2 minutes)

**From ANY phone:**

1. Dial: **+1-415-299-7283**
2. Listen for: "Ground station connected. Call established."
3. The call is automatically recorded
4. Hang up when done

**Check recording:**

```bash
# Get the Call SID from Twilio logs, then:
curl "https://satcom-project-eqqi5.ondigitalocean.app/api/call/recordings/CALL_SID"
```

---

## 🎯 **SWAGGER UI TESTING**

Open: https://satcom-project-eqqi5.ondigitalocean.app/docs

### **1. Make a Call:**

- Click `POST /api/call/make`
- Click "Try it out"
- Request body:
  ```json
  {
    "to_number": "+19788384309"
  }
  ```
- Click "Execute"
- **Copy the Call SID from response!**

### **2. Send Text During Call:**

- Click `POST /api/call/send-text`
- Click "Try it out"
- Request body:
  ```json
  {
    "text": "This is a test transmission from Ground Control"
  }
  ```
- Click "Execute"

### **3. Hang Up:**

- Click `POST /api/call/hangup`
- Click "Try it out"
- Leave empty or add Call SID:
  ```json
  {}
  ```
- Click "Execute"

---

## 📊 **WHAT EACH ENDPOINT DOES**

| Endpoint                         | What It Does          | When To Use                      |
| -------------------------------- | --------------------- | -------------------------------- |
| `POST /api/call/make`            | Makes outgoing call   | Start a call from Ground Control |
| `POST /api/call/send-text`       | Text-to-speech        | Send voice message during call   |
| `POST /api/call/send-audio`      | Play audio file       | Play pre-recorded audio          |
| `POST /api/call/hangup`          | End call              | Terminate active call            |
| `GET /api/call/status`           | Get call info         | Check call status/duration       |
| `GET /api/call/recordings/{sid}` | Get recordings        | Download call audio              |
| `POST /api/call/answer`          | Incoming call handler | Auto-triggered by Twilio         |

---

## 🔑 **UNDERSTANDING CALL SIDS**

**Call SID** = Unique ID for each call (like a tracking number)

Example: `CA17e4ba4400a0df3dc14888fa9b007896`

**Where you get it:**

- When you make a call via `/api/call/make`
- From Twilio's call logs
- From webhooks (incoming calls)

**How to use it:**

- Check status: `/api/call/status?call_sid=CA17e4...`
- Get recordings: `/api/call/recordings/CA17e4...`
- Control specific call: Include in request body

**Important:** Each call gets a NEW Call SID - you can't reuse them!

---

## ⚠️ **COMMON ISSUES & FIXES**

### **"No active call" error**

**Problem:** Trying to send text/audio when no call is active  
**Fix:** Make a call first using `/api/call/make`

### **"CallInstance object has no attribute" error**

**Problem:** Using old/invalid Call SID  
**Fix:** Get fresh Call SID from new call

### **Call doesn't ring**

**Problem:** Twilio number not configured  
**Fix:** Already configured! Should work fine.

### **Can't hear text-to-speech**

**Problem:** Call not answered  
**Fix:** Answer the phone before sending text

---

## 💰 **COSTS**

**Current Setup:**

- DigitalOcean: **$5/month** (API hosting)
- Twilio Numbers: **$1/month each** ($2 total)
- Twilio Calls: **~$0.01-0.02/minute**

**Demo Costs:** Basically free (pennies per test)

---

## 🎬 **DEMO SCRIPT FOR CLIENT**

**"Let me show you our satellite communication system..."**

1. **Make Call:**
   "First, Ground Control initiates contact with the satellite..."
   → Run `/api/call/make`

2. **Send Message:**
   "Now we're sending a mission directive via text-to-speech..."
   → Run `/api/call/send-text` with mission message

3. **Show Recording:**
   "All transmissions are automatically recorded for mission logs..."
   → Run `/api/call/recordings`

4. **Incoming Call:**
   "The satellite can also initiate contact with Ground Control..."
   → Call +1-415-299-7283 from phone

**Total Demo Time:** 2-3 minutes  
**Wow Factor:** 🚀🚀🚀

---

## ✅ **READY CHECKLIST**

Before your demo:

- [ ] Test all endpoints once
- [ ] Check recordings are accessible
- [ ] Verify both numbers work
- [ ] Have Call SID examples ready
- [ ] Test incoming call feature
- [ ] Open Swagger UI in browser tab
- [ ] Have curl commands ready

---

**API URL:** https://satcom-project-eqqi5.ondigitalocean.app  
**Docs:** https://satcom-project-eqqi5.ondigitalocean.app/docs  
**Status:** ✅ PRODUCTION READY

**Last Updated:** October 28, 2025  
**Version:** 1.0.0
