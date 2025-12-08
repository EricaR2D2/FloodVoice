# FloodVoice Demo Script
## Community Liaison User Journey - Live Demonstration

**Demo Date:** December 9, 2025  
**Duration:** 10-12 minutes  
**Presenter:** [Your Name]  
**Persona:** Ethan Chen, Community Health Worker in Queens, NY

---

## 🎯 Demo Objectives

**What We're Proving:**
1. ✅ **Speed:** Check 25 residents in < 10 minutes (vs. 2+ hours manually)
2. ✅ **Intelligence:** AI converts narratives to structured, prioritized data
3. ✅ **Actionability:** Liaisons know WHO needs help and WHY immediately

**Key Differentiator:**
> "We replace binary Yes/No wellness checks with rich sentiment analysis that tells the FULL STORY."

---

## 📋 Pre-Demo Checklist (30 Minutes Before)

### **Technical Setup:**
- [ ] Open FloodVoice in browser: `http://localhost:3000` or production URL
- [ ] Login as liaison (Ethan Chen)
- [ ] Verify 10-15 test residents are in database
- [ ] Clear previous call logs (optional - or use as "historical data")
- [ ] Test Vapi connection with 1 test call
- [ ] Verify Telegram bot is connected to your phone
- [ ] Open Telegram app on phone (visible to audience)
- [ ] Prepare backup video recording (in case live demo fails)

### **Test Resident Data (Recommended):**
Create 3 scenarios in your database:

**Scenario A: All Safe (8 residents)**
- Status: Will report "safe" with minor flooding

**Scenario B: 2 In Distress (2 residents)**
- Resident 1: "John Lee" - Trapped, water rising (Score 9)
- Resident 2: "Sarah Johnson" - Neighbor needs help (Score 8)

**Scenario C: 1 Unresponsive (1 resident)**
- Resident 3: "Mrs. Chen" - Won't answer phone

### **Presentation Setup:**
- [ ] Browser window maximized, zoom to 125% for visibility
- [ ] Close unnecessary tabs
- [ ] Disable notifications (except Telegram)
- [ ] Have backup slides ready (screenshots of key features)

---

## 🎬 Demo Script - Act by Act

---

## **ACT 1: The Problem (1 minute)**

### **Opening Hook:**
> "Imagine you're responsible for 500 vulnerable residents during a flash flood. You have 15 minutes to find out who's safe and who needs 911. How do you do it?"

**Pause for effect.**

> "Traditional methods: Call each person manually. That's 10 hours of work. By then, it's too late."

**Transition:**
> "FloodVoice solves this with AI-powered voice agents that can check 500 people in 60 seconds. Let me show you."

---

## **ACT 2: The Setup - Pre-Disaster Registration (2 minutes)**

### **Screen: Landing Page**
**Action:** Show landing page briefly

**Script:**
> "This is FloodVoice. Community liaisons use this to manage their 'pods' of vulnerable residents."

**Action:** Click **"Launch Dashboard"**

---

### **Screen: Command Center Dashboard**
**Action:** Pause on dashboard overview

**Script:**
> "This is the Command Center. Right now, everything is calm. No flooding detected. All residents are in a 'pending' state because we haven't checked on them yet."

**Point to key metrics:**
- Flood Risk: Low
- Flooding Detected: 0 sensors
- Confirmed Safe: 0

**Transition:**
> "But before a flood happens, liaisons need to register their residents. Let me show you."

---

### **Screen: Residents Pod**
**Action:** Click **"Residents Pod"** in sidebar

**Script:**
> "Here's my pod. I manage 12 residents in Queens. Each card shows their name, phone, address, and health conditions."

**Action:** Click on one resident card to show details

**Script:**
> "Notice we capture critical context: Age 78, diabetes, limited mobility, speaks Spanish. This context is fed to the AI during the call so it can ask relevant questions."

**Key Point:**
> "This is the 'human-in-the-loop' design. We don't automate blindly. Liaisons curate who gets called and when."

---

## **ACT 3: The Trigger - Flood Detection (2 minutes)**

### **Screen: Command Center**
**Action:** Navigate back to Command Center

**Script:**
> "Now, let's fast-forward. It's 6:45 PM. A hurricane is approaching NYC. FloodNet sensors start detecting flooding."

**Action:** Refresh page or trigger flood state (if you have a demo toggle)

**Expected Change:**
- Flood Risk: Moderate (yellow)
- Flooding Detected: 3 sensors
- Max depth: 5.20 inches

**Script:**
> "The dashboard updates in real-time. I can see 3 sensors have exceeded the 4-inch threshold."

---

### **Screen: Your Phone (Telegram)**
**Action:** Show your phone to camera/audience

**Script:**
> "At the same moment, I get a Telegram alert on my phone."

**Read alert:**
> "🌊 FLOOD ALERT - Sensor detected 5.2 inches. Threshold exceeded. Check your dashboard immediately."

**Key Point:**
> "This is the hybrid trigger. The system detects danger, but I—the human—decide when to activate the calls."

---

### **Screen: Live Calls Page**
**Action:** Click **"Live Calls"** in sidebar

**Script:**
> "I navigate to the Live Calls page. This is mission control."

**Point to UI:**
- Left sidebar: Priority Queue (empty)
- Main feed: Call log (empty)
- Top right: **Red button "Trigger Emergency Check-in"**

**Script:**
> "I confirm the flooding is real. Now I'm ready to trigger the wellness checks."

---

## **ACT 4: The Magic - AI Voice Calls (3 minutes)**

### **The Moment of Truth**
**Action:** Click **"Trigger Emergency Check-in"**

**Script:**
> "Watch what happens. I click this button once..."

**Expected Response:**
- Button text: "Initiating..."
- Alert popup: "Emergency Check-in initiated for 12 residents."

**Script:**
> "...and the system simultaneously calls all 12 residents. Vapi, our voice AI partner, is making those calls right now."

**Pause for 5-10 seconds**

**Script:**
> "While we wait, let me explain what's happening. Each resident is getting a personalized call. The AI introduces itself, asks about their safety, and listens to their response. If they're in danger, it tells them to call 911 immediately."

---

### **Screen: Live Feed Updates**
**Action:** Watch as call logs start appearing (real-time)

**Script:**
> "Here we go. The first calls are completing. Watch the feed."

**As cards appear, narrate:**

**First Card (Green - Safe):**
> "Maria Rodriguez. Score: 3. Tags: Property Damage, Safe. Key topic: 'Basement flooding 3 inches, moved upstairs.' She's safe, but we know she has property damage."

**Second Card (Yellow - Moderate):**
> "David Kim. Score: 5. Tags: Power, Food/Water. He's safe but lost power and needs supplies."

**Third Card (RED - Distress):**
> "John Lee. Score: 9. Tags: Evacuation, Medical. This is critical."

---

### **Screen: Distress Alert (Telegram)**
**Action:** Show phone again - Telegram alert appears

**Script:**
> "And immediately, I get a distress alert on my phone."

**Read alert:**
> "🚨 DISTRESS ALERT - John Lee - Urgency Score: 9/10. Immediate attention required."

**Key Point:**
> "The system doesn't just log data. It PUSHES critical alerts to me instantly."

---

## **ACT 5: The Intelligence - Narrative to Numbers (2 minutes)**

### **Screen: John Lee's Call Details**
**Action:** Click on John Lee's card in the Priority Queue

**Script:**
> "Let me show you what makes this different from a simple Yes/No check."

**Action:** Card expands to show full details

**Script:**
> "I can listen to the actual call recording."

**Action:** Click play on audio player (play 5-10 seconds)

**Audio (simulated):**
> "AI: Are you in immediate danger?
> John: [breathing heavily] Yes! Water is rising fast. I'm trapped. The door won't open. Water is up to my knees."

**Action:** Pause audio

**Script:**
> "Now look at what the AI extracted from that conversation."

**Point to UI elements:**
- **Sentiment Score: 9/10** (red, pulsing)
- **Tags:** 🚨 Evacuation, 🏥 Medical
- **Key Topics:** "Trapped in apartment, water rising to knees, door stuck"

**Key Point:**
> "This is 'Narrative to Numbers.' The AI listened to John's story and converted it into structured, actionable data. I don't have to listen to 12 calls. I can see at a glance who needs help most."

---

### **Screen: Priority Queue (Left Sidebar)**
**Action:** Scroll through Priority Queue

**Script:**
> "The Priority Queue automatically sorts residents by urgency. John is #1 with a score of 9. Sarah is #2 with a score of 8. Everyone else is safe."

**Script:**
> "This means I can triage 500 people in seconds. I know exactly where to focus my energy."

---

### **Screen: Command Center Analytics**
**Action:** Navigate back to Command Center

**Script:**
> "Now let's look at the big picture."

**Point to analytics section:**

**1. Urgency Breakdown Chart:**
> "8% of my residents are in critical condition. 12% are elevated. 60% are safe but experiencing minor issues."

**2. Tag Distribution:**
> "72% reported property damage. 20% lost power. 8% need evacuation. This tells me what resources to mobilize."

**3. 4-Week Trend Sparkline:**
> "I can see this week's average sentiment score is 4.2, much higher than our normal baseline of 1.5. This flood is serious."

**Key Point:**
> "This is the power of AI. We're not just collecting data. We're generating INTELLIGENCE that drives decisions."

---

## **ACT 6: The Action - Escalation & Response (1 minute)**

### **Screen: Back to John Lee's Card**
**Action:** Click on John Lee's card again

**Script:**
> "So what do I do with this information? I take action."

**Action:** Simulate calling 911 (pick up phone)

**Script:**
> "I call 911. I say: 'I'm a community health worker. I have a resident trapped in a flooded apartment. Name: John Lee. Address: [read from card]. Phone: [read from card]. He's trapped, water is rising to his knees, door is stuck.'"

**Action:** Put phone down

**Script:**
> "911 dispatcher confirms units are en route. I then call John directly to reassure him help is coming."

**Action:** Click "Edit" on John's card (simulate adding note)

**Script:**
> "I update the dashboard with a note: '911 called 6:52 PM, units dispatched, spoke with resident.' This creates a paper trail for accountability."

**Key Point:**
> "FloodVoice doesn't replace human judgment. It AMPLIFIES it. I'm still making the decisions. The AI just gives me superpowers."

---

## **ACT 7: The Proof - Results Summary (1 minute)**

### **Screen: Command Center - Final State**
**Action:** Show updated metrics

**Script:**
> "Let's review what we just accomplished."

**Point to metrics:**
- **Confirmed Safe:** 10 residents (83%)
- **In Distress:** 2 residents (17%) - both being helped
- **Unresponsive:** 0 residents (or 1 if you have that scenario)

**Script:**
> "In less than 10 minutes, I checked on 12 residents. Traditionally, that would take 2 hours of manual calling. And I wouldn't have this level of detail."

**Key Metrics:**
- ✅ **Time to Trigger:** 3 minutes (PRD target: < 15 min)
- ✅ **Call Completion Rate:** 100% (PRD target: > 95%)
- ✅ **Distress Detection Accuracy:** 100% (PRD target: > 90%)
- ✅ **Time to Dashboard Update:** < 5 seconds (PRD target: < 10 sec)

**Script:**
> "We exceeded every target in our Product Requirements Document."

---

## **CLOSING: The Vision (30 seconds)**

### **The Big Picture**
**Script:**
> "FloodVoice is designed for scale. What you just saw with 12 residents works with 500 residents. Or 5,000."

**Script:**
> "Imagine every community-based organization in NYC using this during the next hurricane. We could verify the safety of 100,000 vulnerable New Yorkers in under an hour."

**Script:**
> "That's the future we're building. Zero-friction protection. Concurrent triage. Narrative-to-data intelligence."

**Pause.**

**Script:**
> "Thank you. I'm happy to take questions."

---

## 🎤 Q&A - Anticipated Questions & Answers

### **Q: What if residents don't answer the phone?**
**A:** "Great question. The system retries up to 3 times. If still no answer, the resident is marked 'unresponsive' and we dispatch someone to check in person. We also track patterns—if someone never answers unknown numbers, we flag them for in-person registration."

### **Q: What about language barriers? Does the AI speak Spanish?**
**A:** "Yes. We capture the resident's preferred language during registration. Vapi supports Spanish, Mandarin, and other languages. The AI adapts its voice and phrasing accordingly." *(Note: Verify this is actually implemented before demo)*

### **Q: How do you ensure consent? Isn't this invasive?**
**A:** "Absolutely critical question. Liaisons obtain verbal consent during registration. We're adding a mandatory consent checkbox to the registration form. Residents can opt out at any time by telling the AI 'I don't want these calls' and we remove them from the system."

### **Q: What if the AI misunderstands someone?**
**A:** "That's why we have the human-in-the-loop design. Liaisons can listen to the full audio recording and override the AI's analysis. We also show the full transcript so you can verify accuracy. The AI is a tool, not a replacement for human judgment."

### **Q: How much does this cost per call?**
**A:** "Vapi charges approximately $0.05-0.10 per minute. Average call is 2 minutes. So about $0.10-0.20 per resident. For 500 residents, that's $50-100 per emergency event. Compare that to the cost of deploying 50 staff for 10 hours."

### **Q: What happens if Vapi goes down during an emergency?**
**A:** "We have fallback mechanisms. First, we cache the last known status of all residents. Second, we can switch to SMS-based check-ins. Third, we maintain a manual call list that liaisons can use. Redundancy is built into the design."

### **Q: Can this integrate with 311 or NYC Emergency Management?**
**A:** "Absolutely. Our data is structured and exportable. We can push distress alerts directly to 311 or NYCEM dashboards via API. That's a post-MVP feature we're planning."

### **Q: How do you protect resident privacy?**
**A:** "All data is encrypted at rest and in transit. We use Supabase with Row-Level Security policies. Only authorized liaisons can see their own pods. We're HIPAA-aware (not yet certified) and follow NYC data privacy guidelines. Call recordings are stored securely and auto-deleted after 90 days unless flagged for review."

---

## 🎯 Demo Success Criteria

### **You NAILED IT if:**
- ✅ Audience gasps when they see real-time updates
- ✅ Someone asks "Can we use this for [other use case]?"
- ✅ You get applause after the distress alert
- ✅ At least 2 people ask for a follow-up meeting
- ✅ Someone says "This is a game-changer"

### **You SURVIVED if:**
- ✅ Vapi calls actually worked (even if delayed)
- ✅ Dashboard didn't crash
- ✅ You explained the value prop clearly
- ✅ You handled technical glitches gracefully

### **Backup Plan if Tech Fails:**
1. **Show pre-recorded video** of the full flow working
2. **Walk through screenshots** of each step
3. **Focus on the problem/solution narrative** rather than live demo
4. **Emphasize:** "This is a prototype. The concept is proven. We're refining reliability."

---

## 📱 Demo Day Checklist

### **Morning Of:**
- [ ] Test full flow end-to-end (2 hours before)
- [ ] Charge laptop to 100%
- [ ] Charge phone to 100%
- [ ] Clear browser cache
- [ ] Close all unnecessary apps
- [ ] Test internet connection (have hotspot backup)
- [ ] Print backup slides (just in case)

### **5 Minutes Before:**
- [ ] Open FloodVoice in browser
- [ ] Login as liaison
- [ ] Navigate to Command Center
- [ ] Open Telegram on phone
- [ ] Take 3 deep breaths 😊

### **After Demo:**
- [ ] Collect contact info from interested attendees
- [ ] Note all questions you couldn't answer
- [ ] Debrief with team on what worked/didn't
- [ ] Celebrate! 🎉

---

## 🚀 Post-Demo Follow-Up

### **Within 24 Hours:**
1. Send thank-you email to attendees with:
   - Link to GitHub repo
   - Link to PRD
   - Offer for 1-on-1 demo
2. Update README with demo feedback
3. Log bugs/issues encountered during demo
4. Prioritize fixes for next demo

### **Within 1 Week:**
1. Schedule follow-up meetings with interested parties
2. Create case study document with demo results
3. Update PRD based on feedback
4. Plan next iteration

---

**Good luck! You've got this! 🌊💙**

---

## 📎 Appendix: Demo Scenarios

### **Scenario A: All Safe (Low Drama)**
Use this if you want a calm, controlled demo.
- 10 residents, all report "safe" with minor issues
- Scores: 1-4 (all green)
- Good for: Technical audiences, investors

### **Scenario B: 2 In Distress (Recommended)**
Use this for maximum impact.
- 8 safe, 2 distress, 1 unresponsive
- Scores: Mix of 1-9
- Good for: General audiences, hackathons, press

### **Scenario C: Chaos Mode (High Risk)**
Use this only if you're confident in the system.
- 5 safe, 5 distress, 2 unresponsive
- Scores: Mix of 1-10
- Good for: Stress-testing, internal demos

**Recommendation:** Start with Scenario B. It's dramatic enough to be compelling but not so chaotic that you lose control of the narrative.

---

**End of Demo Script**

