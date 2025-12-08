# Community Liaison User Journey Map
## FloodVoice Platform - Complete Walkthrough

**Persona:** Ethan Chen, Community Health Worker  
**Context:** Manages a "pod" of 25 vulnerable residents in Queens, NY  
**Goal:** Ensure all residents are safe during a flash flood event

---

## 🎯 Journey Overview

```
PRE-DISASTER → FLOOD DETECTION → EMERGENCY RESPONSE → REAL-TIME MONITORING → ESCALATION → POST-EVENT
   (Days)          (Minutes)           (Seconds)            (Minutes)           (Immediate)      (Hours)
```

---

## PHASE 1: Pre-Disaster Registration (Days/Weeks Before)

### Step 1.1: Initial Access
**Page:** Landing Page (`/`)  
**Action:** Ethan visits `floodvoice.app` and clicks **"Launch Dashboard"**

**UI Elements:**
- Hero text: "FloodVoice" with animated blur effect
- Stats: "< 2 min Response Time | 85+ Active Sensors | Voice API Ready"
- CTA Button: "Launch Dashboard" (white, rounded, glowing)

**User Emotion:** 😊 Curious, hopeful about new tool

---

### Step 1.2: Dashboard Overview
**Page:** Command Center (`/dashboard`)  
**Action:** Ethan sees the main dashboard with 5 key metrics

**UI Elements:**
- **Flood Risk Card:** Shows "Low" (green) with "85 sensors clear"
- **Flooding Detected Card:** Shows "0 sensors" (normal state)
- **In Distress:** 0 residents
- **Pending Response:** 0 residents
- **Confirmed Safe:** 0 residents (empty pod)

**Sidebar Navigation:**
- Command Center (active)
- Live Calls
- **Residents Pod** ← Ethan clicks here
- FloodNet Map
- Settings

**User Emotion:** 😐 Neutral, exploring interface

---

### Step 1.3: Add First Resident
**Page:** Residents Pod (`/dashboard/residents`)  
**Action:** Clicks **"+ Add Resident"** button (top right)

**Modal Form Fields:**
1. **Name:** "Maria Rodriguez" (required)
2. **Phone Number:** "718-555-0123" (required, auto-formats to E.164)
3. **Age:** 78
4. **Address:** "123 Basement Apt, Queens, NY 11372"
5. **ZIP Code:** "11372" (used for flood zone mapping)
6. **Health Conditions:** "Diabetes, limited mobility, uses walker"
7. **Language:** Dropdown (English, Spanish, Mandarin) → Selects "Spanish"

**Missing Element (PRD Gap):**
- ⚠️ **Consent Checkbox:** "I certify I have obtained verbal consent from this resident to receive emergency calls" (NOT IMPLEMENTED)

**Action:** Clicks **"Save Resident"**

**System Response:**
- Resident card appears in grid
- Shows: Name, Phone, Age, Address, Status badge ("Pending" - gray)
- Action buttons: Edit, Delete, Call

**User Emotion:** 😊 Satisfied, productive

---

### Step 1.4: Bulk Registration
**Action:** Ethan repeats Step 1.3 for 24 more residents

**Time Investment:** ~15 minutes for 25 residents

**Final State:**
- Residents Pod shows 25 cards in grid layout
- All status: "Pending" (no calls made yet)
- Organized by most recent first

**User Emotion:** 😅 Tired but accomplished

---

## PHASE 2: Flood Detection & Alert (Real-Time)

### Step 2.1: FloodNet Sensor Triggers
**System Event:** Hurricane approaching NYC  
**Time:** 6:45 PM, October 15, 2025

**Backend Process:**
1. FloodNet sensor `dev_id_nyc_floodnet_deployment_1` detects 5.2 inches of water
2. Cron job (`/api/cron/floodnet-monitor`) runs every 5 minutes
3. Checks: `currentDepth (5.2) >= THRESHOLD (4.0)` → TRUE
4. Queries Supabase for all liaisons with `telegram_chat_id`
5. Calls `/lib/telegram.ts` → `sendFloodAlert()`

**Telegram Message Sent:**
```
🌊 FLOOD ALERT
Sensor: dev_id_nyc_floodnet_deployment_1
Current Depth: 5.2 inches
Time: 6:45 PM

⚠️ Threshold exceeded. Check your dashboard immediately.
```

**User Emotion:** 😰 Alarmed, urgent

---

### Step 2.2: Liaison Receives Alert
**Device:** Ethan's phone (Telegram app)  
**Action:** Notification pops up, Ethan clicks it

**User Thought:** *"This is real. I need to check on my residents NOW."*

**Action:** Opens laptop, navigates to `floodvoice.app/dashboard`

**User Emotion:** 😟 Anxious, focused

---

### Step 2.3: Dashboard Shows Flood Risk
**Page:** Command Center (`/dashboard`)  
**Visual Changes:**

**Flood Risk Card:**
- Color: Yellow border (was green)
- Text: "Moderate" (was "Low")
- Subtext: "Max depth: 5.20 in" (was "85 sensors clear")

**Flooding Detected Card:**
- Shows: "3 sensors" (red, pulsing)
- Clickable to see sensor details

**FloodNet Map:**
- 3 sensors show red markers (flooding)
- 82 sensors show green markers (normal)
- Ethan's ZIP code (11372) is highlighted

**User Emotion:** 😨 Concerned, ready to act

---

## PHASE 3: Emergency Response - Manual Trigger

### Step 3.1: Navigate to Live Calls
**Action:** Ethan clicks **"Live Calls"** in sidebar

**Page:** Live Calls (`/dashboard/calls`)

**UI Layout:**
- **Left Sidebar (1/3 width):** Priority Queue (empty - no calls yet)
- **Main Feed (2/3 width):** Call log feed (empty)
- **Top Right:** Red glowing button **"Trigger Emergency Check-in"**

**User Thought:** *"I need to confirm this is real before I call everyone. Let me check the map one more time..."*

**Action:** Scrolls down, sees FloodNet graph showing water level rising over past hour

**User Emotion:** 😰 Determined, ready to trigger

---

### Step 3.2: Click "Trigger Emergency Check-in"
**Action:** Clicks red button

**System Confirmation:** Button text changes to "Initiating..."

**Backend Process (`/api/vapi/trigger`):**
1. Queries Supabase: `SELECT * FROM residents WHERE status != 'safe' AND status != 'unresponsive'`
2. Returns 25 residents (Ethan's full pod)
3. Loops through each resident:
   - Formats phone to E.164: `+17185550123`
   - Builds context string: "Age: 78. Language: Spanish. Address: 123 Basement Apt. Health Conditions: Diabetes, limited mobility"
   - Calls Vapi API with assistant config
   - Updates resident status to "pending"
4. Returns: `{ message: "Triggered 25 calls", results: [...] }`

**Frontend Response:**
- Alert popup: "Emergency Check-in initiated for 25 residents."
- Button returns to normal state

**User Emotion:** 😌 Relief, waiting anxiously

---

### Step 3.3: Residents Pod Updates
**Page:** Residents Pod (if Ethan switches tabs)

**Visual Change:**
- All 25 resident cards now show:
  - Status badge: "Pending" (yellow, pulsing)
  - Phone icon animating

**User Emotion:** 😬 Nervous anticipation

---

## PHASE 4: Real-Time Monitoring - Call Analysis

### Step 4.1: First Call Completes (Maria Rodriguez)
**Time:** 6:48 PM (3 minutes after trigger)

**Vapi Call Flow:**
1. **Ring:** Maria's phone rings
2. **Answer:** "¿Hola?" (Maria answers in Spanish)
3. **AI Agent:** "Hi, this is Flood Voice calling for Maria Rodriguez. We are checking on your safety. Are you in any immediate danger?"
4. **Maria:** "No, no danger. But water is coming into my basement. It's up to my ankles."
5. **AI Agent:** "Glad to hear you are safe. How deep would you say the water is?"
6. **Maria:** "Maybe 3 inches? I moved upstairs."
7. **AI Agent:** "Thank you. I've updated your status. Please stay safe."
8. **AI calls function:** `reportStatus("safe", "Safe, but basement flooding 3 inches, moved upstairs")`

**Backend Webhook (`/api/vapi/webhook`):**
1. Receives `function-call` event
2. Extracts: `status: "safe"`, `summary: "Safe, but basement flooding 3 inches"`
3. Updates Supabase: `UPDATE residents SET status = 'safe' WHERE id = [maria_id]`
4. Inserts call log: `INSERT INTO call_logs (resident_id, summary, risk_label) VALUES (...)`
5. Receives `end-of-call-report` event with transcript and recording URL
6. Calls Gemini AI (`/lib/gemini.ts`):
   - Analyzes transcript
   - Returns: `{ tags: ["Property Damage", "Safe"], sentiment_score: 3, key_topics: "Basement flooding 3 inches, resident moved upstairs" }`
7. Updates call log with AI analysis

**Frontend Real-Time Update (WebSocket):**

**Live Calls Page:**
- **Call Log Feed:** New card appears at top
  - Name: "Maria Rodriguez"
  - Time: "just now"
  - Score badge: "3" (green)
  - Key topics: "Basement flooding 3 inches, resident moved upstairs"
  - Tags: 🏠 Prop, ✅ Safe

**Command Center:**
- **Confirmed Safe:** 1 (was 0)
- **Pending Response:** 24 (was 25)

**User Emotion:** 😊 Relieved, encouraged

---

### Step 4.2: Multiple Calls Complete Simultaneously
**Time:** 6:48-6:52 PM (next 4 minutes)

**Call Results:**
- 20 residents: Status "safe" (scores 1-4)
- 3 residents: Status "pending" (no answer, retrying)
- 2 residents: Status "distress" (scores 8-9) ⚠️

**Live Feed Updates:**
- Cards stream in real-time
- Sorted by urgency score (highest first)
- Green cards (safe) appear at bottom
- Red cards (distress) appear at top with pulsing animation

**Priority Queue (Left Sidebar):**
- Shows top 10 residents by urgency score
- **#1: John Lee - Score 9** (red, pulsing)
- **#2: Sarah Johnson - Score 8** (red)
- #3-10: Scores 4-6 (yellow/orange)

**User Emotion:** 😰 Focused on distress cases

---

## PHASE 5: Escalation - Distress Response

### Step 5.1: Distress Alert (John Lee)
**Time:** 6:49 PM

**Telegram Alert:**
```
🚨 DISTRESS ALERT
Resident: John Lee
Urgency Score: 9/10
Time: 6:49 PM

⚠️ Immediate attention required. Check dashboard now.
```

**User Action:** Ethan's phone buzzes, he sees alert

**User Emotion:** 😱 Alarmed, urgent

---

### Step 5.2: Review Distress Call
**Page:** Live Calls (`/dashboard/calls`)

**Action:** Clicks on John Lee's card in Priority Queue

**Card Expands:**
- **Audio Player:** Shows recording with play button
- **Full Transcript:**
  ```
  AI: "Hi, this is Flood Voice calling for John Lee. Are you in any immediate danger?"
  John: [breathing heavily] "Yes! Water is rising fast. I'm trapped in my apartment.
         The door won't open. Water is up to my knees now."
  AI: "Please hang up and call 911 immediately. This is a life-threatening emergency."
  John: "Okay, okay, I will!"
  [Call ends]
  ```
- **Tags:** 🚨 Evacuation, 🏥 Medical
- **Key Topics:** "Trapped in apartment, water rising to knees, door stuck"

**User Emotion:** 😨 Panicked, must act NOW

---

### Step 5.3: Escalation Actions
**Action:** Ethan immediately:

1. **Calls 911:**
   - "I'm a community health worker. I have a resident trapped in a flooded apartment."
   - Provides: Name (John Lee), Address (from resident card), Phone number
   - 911 dispatcher confirms units en route

2. **Calls John directly:**
   - "John, it's Ethan from the community center. Help is on the way. Stay calm."
   - John confirms he called 911 too

3. **Updates Dashboard:**
   - Clicks "Edit" on John's resident card
   - Adds note: "911 called 6:50 PM, units dispatched, spoke with resident"
   - Status remains "distress" (will update to "safe" after rescue)

**User Emotion:** 😰 Stressed but focused, doing his job

---

### Step 5.4: Second Distress Case (Sarah Johnson)
**Similar flow for Sarah (Score 8):**
- Transcript: "I'm okay but my elderly neighbor is stuck. Can someone check on her?"
- Ethan calls Sarah, gets neighbor's address
- Dispatches local volunteer to check

**User Emotion:** 😓 Exhausted but determined

---

## PHASE 6: Post-Event Review & Analysis

### Step 6.1: All Calls Complete
**Time:** 7:05 PM (20 minutes after trigger)

**Final Status:**
- **Confirmed Safe:** 22 residents
- **In Distress:** 2 residents (being helped)
- **Unresponsive:** 1 resident (no answer after 3 retries)

**Action:** Ethan switches to Command Center to review analytics

---

### Step 6.2: Analytics Review
**Page:** Command Center (`/dashboard`)

**Narrative to Numbers Section:**

1. **Urgency Breakdown Chart:**
   - Critical (8-10): 2 residents (8%)
   - Elevated (6-7): 3 residents (12%)
   - Moderate (4-5): 5 residents (20%)
   - Safe (1-3): 15 residents (60%)

2. **Tag Distribution:**
   - Property Damage: 18 residents (72%)
   - Safe: 15 residents (60%)
   - Evacuation: 2 residents (8%)
   - Medical: 1 resident (4%)
   - Power: 5 residents (20%)

3. **4-Week Trend Sparkline:**
   - Shows average sentiment score over past 4 weeks
   - This week: 4.2 (elevated due to flood)
   - Previous weeks: 1.5-2.0 (normal)

**User Insight:** *"Most residents are safe but experiencing property damage. Need to coordinate cleanup resources."*

**User Emotion:** 😌 Relieved, analytical

---

### Step 6.3: Follow-Up Actions
**Next Day (October 16):**

1. **Update Unresponsive Resident:**
   - Ethan visits Mrs. Chen's apartment in person
   - She's safe, just doesn't answer unknown numbers
   - Updates status to "safe" manually

2. **Coordinate Resources:**
   - Uses Tag Distribution data to request:
     - 18 water pumps for basements
     - 5 generators for power outages
   - Shares analytics with CBO director

3. **Update Resident Information:**
   - Adds notes to each resident card with specific needs
   - Flags 3 residents for priority follow-up next flood

**User Emotion:** 😊 Accomplished, prepared for next time

---

## 📊 Journey Metrics Summary

| Metric | Value | PRD Target | Status |
|--------|-------|------------|--------|
| **Time to Trigger** | 3 minutes | < 15 min | ✅ Exceeded |
| **Call Completion Rate** | 96% (24/25) | > 95% | ✅ Met |
| **Time to Dashboard Update** | < 5 seconds | < 10 sec | ✅ Exceeded |
| **Distress Detection Accuracy** | 100% (2/2) | > 90% | ✅ Exceeded |
| **Liaison Response Time** | 1 minute | N/A | ✅ Excellent |

---

## 🎯 Key Touchpoints & Pain Points

### ✅ **What Works Well:**
1. **Real-time updates** - Dashboard feels alive, no refresh needed
2. **Priority Queue** - Immediately shows who needs help most
3. **Telegram alerts** - Liaison doesn't miss critical events
4. **Audio playback** - Can verify AI analysis by listening
5. **Batch calling** - 25 residents checked in 7 minutes vs. 2+ hours manually

### ⚠️ **Pain Points (Opportunities):**
1. **No consent checkbox** - Liaison must track consent separately
2. **No one-click 911** - Must manually call and provide info
3. **No nearby liaison finder** - Can't easily delegate to neighbors
4. **No multi-language Vapi confirmation** - Unclear if Spanish works
5. **No CBO coordinator view** - Director can't see all liaisons' pods

---

## 🚀 Recommended Improvements

### **High Priority (Pre-Demo):**
1. Add consent checkbox to resident registration
2. Test Spanish language Vapi assistant
3. Create demo script with 3 scenarios (all safe, 2 distress, 1 unresponsive)

### **Medium Priority (Post-Demo):**
1. Add "Call 911" button with pre-filled resident info
2. Build CBO coordinator dashboard (multi-liaison view)
3. Add FVI score integration from old repo

### **Low Priority (Future):**
1. Nearby liaison finder by ZIP code
2. SMS fallback if Telegram fails
3. Export analytics to PDF for grant reports

---

**End of User Journey Map**

