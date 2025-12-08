# FloodVoice Demo - Technical Setup Guide
**Complete setup instructions for preparing the demo environment**

---

## 🎯 Goal
Create a controlled demo environment with 10-15 test residents that will produce predictable, impressive results during the live demo.

---

## 📋 Prerequisites

### **Required:**
- ✅ FloodVoice app running locally or deployed
- ✅ Supabase project configured
- ✅ Vapi account with phone number
- ✅ Google Gemini API key
- ✅ Telegram bot token
- ✅ Test phone numbers (can use your own, teammates', or Vapi test numbers)

### **Recommended:**
- ✅ Backup video recording of successful demo run
- ✅ Screenshots of each key screen
- ✅ Hotspot on phone (backup internet)

---

## 🗄️ Step 1: Prepare Database

### **1.1: Clear Old Data (Optional)**
If you have old test data, clean it up:

```sql
-- Run in Supabase SQL Editor
DELETE FROM call_logs;
DELETE FROM residents;
```

### **1.2: Create Test Liaison Profile**
```sql
-- Insert your liaison profile
INSERT INTO profiles (id, name, email, telegram_chat_id, created_at)
VALUES (
  'YOUR_SUPABASE_USER_ID', -- Get this from Supabase Auth
  'Ethan Chen',
  'ethan.chen@demo.floodvoice.app',
  'YOUR_TELEGRAM_CHAT_ID', -- Get from @userinfobot on Telegram
  NOW()
);
```

**How to get your Telegram Chat ID:**
1. Open Telegram
2. Search for `@userinfobot`
3. Start chat, it will reply with your ID
4. Copy the number (e.g., `8414933635`)

### **1.3: Create Test Residents**

**Scenario B: 2 In Distress (Recommended)**

```sql
-- Safe Residents (Scores 1-5)
INSERT INTO residents (name, phone_number, age, address, zip_code, health_conditions, language, status, liaison_id)
VALUES
  ('Maria Rodriguez', '+1-555-0101', 78, '123 Basement Apt, Queens, NY', '11372', 'Diabetes, limited mobility', 'Spanish', 'pending', 'YOUR_LIAISON_ID'),
  ('David Kim', '+1-555-0102', 65, '456 Oak St, Queens, NY', '11372', 'Asthma', 'English', 'pending', 'YOUR_LIAISON_ID'),
  ('Lisa Chen', '+1-555-0103', 82, '789 Pine Ave, Queens, NY', '11372', 'Heart condition', 'Mandarin', 'pending', 'YOUR_LIAISON_ID'),
  ('Robert Johnson', '+1-555-0104', 70, '321 Maple Dr, Queens, NY', '11372', 'None', 'English', 'pending', 'YOUR_LIAISON_ID'),
  ('Ana Martinez', '+1-555-0105', 75, '654 Elm St, Queens, NY', '11372', 'Arthritis', 'Spanish', 'pending', 'YOUR_LIAISON_ID'),
  ('Michael Brown', '+1-555-0106', 68, '987 Cedar Ln, Queens, NY', '11372', 'Diabetes', 'English', 'pending', 'YOUR_LIAISON_ID'),
  ('Sophia Lee', '+1-555-0107', 73, '147 Birch Rd, Queens, NY', '11372', 'None', 'English', 'pending', 'YOUR_LIAISON_ID'),
  ('James Wilson', '+1-555-0108', 80, '258 Spruce Ct, Queens, NY', '11372', 'COPD', 'English', 'pending', 'YOUR_LIAISON_ID');

-- Distress Residents (Scores 8-9)
INSERT INTO residents (name, phone_number, age, address, zip_code, health_conditions, language, status, liaison_id)
VALUES
  ('John Lee', '+1-555-0109', 85, '369 Willow Way, Queens, NY', '11372', 'Wheelchair user, heart condition', 'English', 'pending', 'YOUR_LIAISON_ID'),
  ('Sarah Johnson', '+1-555-0110', 77, '741 Aspen Blvd, Queens, NY', '11372', 'Dementia, lives alone', 'English', 'pending', 'YOUR_LIAISON_ID');

-- Unresponsive Resident
INSERT INTO residents (name, phone_number, age, address, zip_code, health_conditions, language, status, liaison_id)
VALUES
  ('Mrs. Chen', '+1-555-0111', 90, '852 Redwood Pl, Queens, NY', '11372', 'Hard of hearing', 'Mandarin', 'pending', 'YOUR_LIAISON_ID');
```

**⚠️ IMPORTANT: Replace Phone Numbers**

For a real demo, you have 3 options:

**Option A: Use Real Team Phone Numbers**
- Assign each teammate a resident persona
- They answer the call and follow a script
- **Pros:** Most realistic
- **Cons:** Requires coordination

**Option B: Use Vapi Test Numbers**
- Vapi provides test numbers that auto-respond
- Check Vapi documentation for test numbers
- **Pros:** No human coordination needed
- **Cons:** Less realistic

**Option C: Use Your Own Phone Multiple Times**
- Use your phone for all residents
- Answer each call with different persona
- **Pros:** Full control
- **Cons:** Time-consuming, not scalable for demo

**Recommendation:** Use Option A with 2-3 teammates for distress cases, Option B for safe cases.

---

## 🎭 Step 2: Prepare Call Scripts (For Human Actors)

If using real people to answer calls, give them these scripts:

### **Safe Resident Script (Maria Rodriguez):**
**When AI asks: "Are you in any immediate danger?"**
> "No, no danger. But water is coming into my basement. It's up to my ankles. Maybe 3 inches? I moved upstairs. I'm okay."

**Expected AI Response:**
> "Thank you. I've updated your status. Please stay safe."

**Expected Score:** 2-4 (Safe, Property Damage)

---

### **Distress Resident Script (John Lee):**
**When AI asks: "Are you in any immediate danger?"**
> [Breathing heavily] "Yes! Water is rising fast. I'm trapped in my apartment. The door won't open. Water is up to my knees now. I can't get out!"

**Expected AI Response:**
> "Please hang up and call 911 immediately. This is a life-threatening emergency."

**Expected Score:** 8-10 (Distress, Evacuation, Medical)

---

### **Unresponsive Resident (Mrs. Chen):**
**Action:** Don't answer the phone. Let it ring.

**Expected Result:** Status remains "pending" or changes to "unresponsive" after retries.

---

## 🔧 Step 3: Configure Vapi Assistant

### **3.1: Verify Assistant Config**
Check `src/app/api/vapi/trigger/route.ts` lines 9-66:

**Key settings:**
- Model: `gpt-4o-mini` (fast, cheap)
- Voice: `11labs` with `sarah` voice (friendly, calm)
- Functions: `reportStatus` with `safe` and `distress` options

### **3.2: Test Single Call**
Before the demo, test with ONE resident:

```bash
# In your terminal
curl -X POST http://localhost:3000/api/vapi/trigger \
  -H "Content-Type: application/json" \
  -d '{"targetResidentId": "MARIA_RODRIGUEZ_ID"}'
```

**Verify:**
- ✅ Call is received
- ✅ AI speaks clearly
- ✅ Webhook updates database
- ✅ Gemini analysis runs
- ✅ Dashboard updates in real-time

---

## 📱 Step 4: Configure Telegram Alerts

### **4.1: Create Telegram Bot**
If you haven't already:

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to create bot
4. Copy the token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Add to `.env.local`: `TELEGRAM_BOT_TOKEN=your_token`

### **4.2: Get Your Chat ID**
1. Search for `@userinfobot` on Telegram
2. Start chat, it replies with your ID
3. Add to your profile in Supabase (Step 1.2)

### **4.3: Test Telegram Alert**
```bash
# Test distress alert
curl -X POST http://localhost:3000/api/test-telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "🚨 TEST ALERT - This is a test"}'
```

**Verify:** You receive the message on your phone.

---

## 🎨 Step 5: Prepare UI for Demo

### **5.1: Browser Settings**
- **Zoom:** 125% (for visibility on projector)
- **Window:** Maximized, full screen
- **Tabs:** Close all except FloodVoice
- **Extensions:** Disable ad blockers, privacy tools (can break WebSockets)

### **5.2: Disable Distractions**
- Turn off email notifications
- Turn off Slack notifications
- Turn off OS notifications (except Telegram)
- Close unnecessary apps

### **5.3: Prepare Backup Materials**
- Screenshot of each key screen
- Pre-recorded video of full demo flow
- Slides with key talking points

---

## 🧪 Step 6: Full Dress Rehearsal

### **6.1: Run Complete Flow (2 Hours Before Demo)**

1. **Start:** Navigate to landing page
2. **Login:** Click "Launch Dashboard"
3. **View Residents:** Navigate to Residents Pod, show resident cards
4. **Trigger Calls:** Navigate to Live Calls, click "Trigger Emergency Check-in"
5. **Monitor Feed:** Watch call logs appear in real-time
6. **Check Telegram:** Verify distress alerts arrive
7. **Review Details:** Click on distress call, play audio, show transcript
8. **View Analytics:** Navigate to Command Center, show charts
9. **Simulate 911:** Pick up phone, read resident info

**Time this!** Should be 8-10 minutes.

### **6.2: Record Backup Video**
If everything works perfectly, record your screen:

**Windows:** Use Xbox Game Bar (Win + G)
**Mac:** Use QuickTime Screen Recording

Save as: `FloodVoice_Demo_Backup.mp4`

---

## ✅ Final Checklist (Morning of Demo)

- [ ] All test residents in database
- [ ] Liaison profile configured with Telegram chat ID
- [ ] Vapi test call successful
- [ ] Telegram alerts working
- [ ] Browser configured (zoom, tabs closed)
- [ ] Laptop charged to 100%
- [ ] Phone charged to 100%
- [ ] Backup video ready
- [ ] Backup slides ready
- [ ] Internet connection tested
- [ ] Hotspot enabled on phone (backup)
- [ ] Demo script printed
- [ ] Quick reference card printed
- [ ] Water bottle nearby 💧
- [ ] Deep breaths taken 😊

---

## 🚨 Troubleshooting

### **Problem: Vapi calls don't trigger**
**Fix:**
1. Check `.env.local` has `VAPI_PRIVATE_KEY` and `VAPI_PHONE_NUMBER_ID`
2. Check Vapi dashboard for account balance
3. Check phone numbers are E.164 format (`+1-555-0101`)
4. Check Vapi logs for errors

### **Problem: Dashboard doesn't update in real-time**
**Fix:**
1. Check browser console for WebSocket errors
2. Refresh page
3. Check Supabase Realtime is enabled
4. Disable browser extensions

### **Problem: Telegram alerts don't arrive**
**Fix:**
1. Check `TELEGRAM_BOT_TOKEN` in `.env.local`
2. Check `telegram_chat_id` in profiles table
3. Check you've started a chat with the bot
4. Check bot has permission to send messages

### **Problem: Gemini analysis fails**
**Fix:**
1. Check `GOOGLE_GEMINI_API_KEY` in `.env.local`
2. Check API quota/billing
3. Check model name is correct (`gemini-2.0-flash-lite`)
4. Fallback: Show transcript without AI analysis

---

**You're ready! Good luck! 🌊💙**

