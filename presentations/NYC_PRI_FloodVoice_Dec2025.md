# FloodVoice: From Voices to Values
## Transforming Qualitative Community Narratives into Actionable Public Health Intelligence

**NYC Preparedness & Recovery Institute (PRI)**  
**Data Collection, Sharing, and Translation Y3Q1 Team Meeting**  
**December 9, 2025**

**Team:** Jessenia, Ethan, Erica, Josue, Kelvin, Shanell  
**Duration:** 7-10 minutes

---

# SLIDE 1: THE PROBLEM (1.5 minutes)

## "During Floods, Vulnerable New Yorkers Are Invisible"

### The Data Gap We're Solving

**Who is affected:**
- **50,000-100,000** basement apartment residents
- **15%** of NYC population aged 65+ (digital divide)
- Non-English speakers, residents with disabilities

**What happened during Hurricane Ida (2021):**
- **11 deaths** in NYC—majority trapped in basement apartments
- **10,000+ calls/hour** overwhelmed 911
- Current text-based alerts (WEA, Notify NYC) failed to reach vulnerable populations

### The Core Challenge

**Emergency responders cannot distinguish between:**

| 🔴 LIFE-THREATENING | 🟡 NON-URGENT |
|---------------------|---------------|
| "Trapped in basement, water at my waist" | "Street is flooded, I'm safe upstairs" |
| Requires immediate rescue | Can wait |

**Result:** Undifferentiated qualitative data → Preventable delays → Loss of life

> **📝 SPEAKER NOTES:**
> - Open with a pause after "invisible" to let it sink in
> - The Ida stat is powerful—11 deaths, most in basements. Let that land.
> - Key point: The 10,000 calls/hour stat shows WHY we need AI triage—humans cannot process this volume
> - Use the table contrast to show the EXACT problem we solve: same channel (voice), but AI helps distinguish urgency
> - Transition: "So how do we make the invisible visible? That's where FloodVoice comes in."

---

# SLIDE 2: THE SOLUTION (1.5 minutes)

## FloodVoice: AI-Powered Community Triage

**One-Line Description:**  
An automated voice-based welfare check system that converts **thousands of qualitative phone conversations** into a **structured, prioritized emergency response dataset** in real-time.

### How It Works (30-Second Overview)

```
FLOOD DETECTED → LIAISONS ALERTED → AI CALLS RESIDENTS → NARRATIVES ANALYZED → TRIAGE DASHBOARD
     ↓                  ↓                   ↓                    ↓                    ↓
FloodNet Sensors → Telegram Alert → Voice AI Welfare → Gemini AI NLP → Priority Queue
(>4" depth)        to CBO Staff     Check Calls       Sentiment Tags    for Responders
```

### Three Key Innovations

1. **Zero-Friction Access:** No app required—works with any phone (landline or cell)
2. **Massive Scale:** 1 liaison can check 500 residents in 60 seconds (vs. 10/hour manually)
3. **Narrative-to-Numbers:** AI extracts sentiment, urgency, and specific needs from natural speech

### Intended Impact
- Identify critical cases within **15 minutes** of flood detection
- Achieve **90% classification accuracy** (safe vs. distress)
- Scale to protect **60,000+ vulnerable NYC residents** via CBO partnerships

> **📝 SPEAKER NOTES:**
> - Read the one-liner slowly—it encapsulates everything
> - Walk through the flow diagram pointing at each step: "Sensors detect → alert sent → AI calls → analyzes → dashboard"
> - Emphasize the 3 innovations with hand gestures (1, 2, 3)
> - Zero-Friction: "Your grandmother doesn't need an iPhone—just her landline"
> - Scale: "Imagine manually calling 500 people. That's 50 hours of work. We do it in 60 seconds."
> - Impact numbers are aspirational but grounded—we have the tech, need the pilot
> - Transition: "Now let me show you the data that powers this..."

---

# SLIDE 3: DATA SOURCES & INTEGRATION (2.5 minutes)

## What Data Do We Use?

| Data Source | Data Type | Qual/Quant | Purpose |
|-------------|-----------|------------|---------|
| **FloodNet NYC Sensors** | Numeric (depth in inches) | Quantitative | Flood detection trigger |
| **Voice Call Audio** | Audio recordings (WAV) | **Qualitative** | Raw resident narratives |
| **Call Transcripts** | Text | **Qualitative** | Spoken words converted to text |
| **Resident Profiles** | Structured (name, age, address, health conditions) | Quantitative | Vulnerability context |
| **AI Sentiment Scores** | Numeric (1-10 scale) | Quantitative | Urgency classification |
| **Need Tags** | Categorical | Quantitative | Medical, Evacuation, Power, etc. |

## How Are They Integrated?

**Real-Time Data Pipeline:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA INTEGRATION FLOW                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │  FloodNet   │     │   Resident  │     │   Liaison   │                │
│  │   Sensors   │     │  Profiles   │     │  Telegram   │                │
│  │  (50+ NYC)  │     │  (Supabase) │     │    Bot      │                │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│  ┌──────────────────────────────────────────────────────┐               │
│  │              TRIGGER: Depth > 4" for 15 min          │               │
│  └──────────────────────────────────────────────────────┘               │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────┐               │
│  │     VAPI VOICE AI: Concurrent Outbound Calls         │               │
│  │     "Hi, this is Flood Voice calling for Maria..."   │               │
│  └──────────────────────────────────────────────────────┘               │
│                            │                                             │
│              ┌─────────────┼─────────────┐                              │
│              ▼             ▼             ▼                              │
│         [Audio]      [Transcript]    [Summary]                          │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────┐               │
│  │           GEMINI AI: NLP & Sentiment Analysis        │               │
│  │     → Sentiment Score (1-10)                         │               │
│  │     → Tags: [Medical, Evacuation, Safe...]           │               │
│  │     → Key Topics: "Water entering basement"          │               │
│  └──────────────────────────────────────────────────────┘               │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────┐               │
│  │       DASHBOARD: Real-Time Priority Queue            │               │
│  │       (WebSocket updates via Supabase Realtime)      │               │
│  └──────────────────────────────────────────────────────┘               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## The Qualitative → Quantitative Transformation

**INPUT (Qualitative - Raw Voice):**
> *"I'm okay, but... the water is coming into my basement. It's about ankle-deep now. I moved my things upstairs."*

**OUTPUT (Quantitative - Structured Data):**
```json
{
  "sentiment_score": 4,
  "tags": ["Property Damage", "Safe"],
  "key_topics": "Basement flooding ankle-deep, resident relocated belongings upstairs",
  "risk_label": "MODERATE",
  "action": "Monitor - No immediate escalation"
}
```

> **📝 SPEAKER NOTES:**
> - This slide is the HEART of the presentation for data scientists
> - Point to the table: "Voice calls and transcripts are qualitative—the AI outputs are quantitative"
> - Walk through the pipeline diagram slowly, pointing at each box
> - The transformation example is KEY: read the input quote aloud with emotion, then show the structured output
> - "This is the core innovation: unstructured human narrative becomes structured, queryable data"
> - Ask rhetorically: "How do we know this person is at moderate risk? The AI scores sentiment at 4/10 and tags it correctly"
> - Transition: "Let me show you exactly how the AI makes these decisions..."

---

# SLIDE 4: IMPLEMENTATION DETAILS (2 minutes)

## Technical Architecture

### Voice AI & Speech Recognition

**How spoken words become structured data:**

1. **Vapi.ai Voice Platform** initiates outbound calls to residents
2. **Real-time transcription** converts speech to text during the call
3. **GPT-4o-mini** (OpenAI) powers the conversational AI agent
4. **ElevenLabs** provides natural voice synthesis ("Sarah" voice)

**Example System Prompt:**
```
You are 'Flood Voice', a calm disaster response assistant.
Your Goal: Verify resident safety and collect flooding conditions.

Conversation Flow:
1. SAFETY FIRST: "Are you in any immediate danger?"
   → If DANGER: Instruct to call 911, report 'distress', end call

2. INVESTIGATION (If Safe):
   → "Is there flooding around your building?"
   → "How deep is the water?"
   → "Is water entering your home?"

3. CLOSE: "I've updated your status. Please stay safe."
```

### NLP & Sentiment Classification

**Google Gemini AI analyzes transcripts with structured prompts:**

```
Sentiment Scoring Rules (1-10):
  1-3: Calm, informational, safe
  4-6: Concerned, anxious, mild needs
  7-8: Distressed, urgent needs, crying
  9-10: Panic, life-threatening, screaming

Fixed Taxonomy (7 Categories):
  - Medical
  - Food/Water
  - Power
  - Evacuation
  - Mental Health
  - Property Damage
  - Safe
```

**Model Fallback Chain for Reliability:**
```
gemini-2.5-flash-lite → gemini-2.5-flash → gemini-2.0-flash-lite → gemini-2.0-flash
```

### Real-Time Dashboard Updates

**Supabase Realtime (WebSocket)** pushes updates instantly:
- New call completed → Dashboard updates in <3 seconds
- Distress detected (score ≥7) → Telegram alert to liaison
- Priority queue auto-sorts by sentiment score

> **📝 SPEAKER NOTES:**
> - For engineers in the room: emphasize the tech stack (Vapi, GPT-4o-mini, ElevenLabs, Gemini)
> - The system prompt is the "brain"—show how it guides the conversation
> - The 7 fixed taxonomy tags are CRITICAL: "We chose these based on NYC emergency response categories"
> - Model fallback chain shows reliability thinking: "If one model is overloaded, we fail over automatically"
> - WebSocket = instant updates. "The moment a call ends, the dashboard updates in under 3 seconds"
> - Transition: "Now let me show you what the dashboard actually looks like..."

---

# SLIDE 5: DATA VISUALIZATION (1 minute)

## How We Inform Response Decisions

### Dashboard Components

| Component | Data Shown | Decision Impact |
|-----------|------------|-----------------|
| **Urgency Breakdown** | Chart: Critical/Elevated/Moderate/Safe | Resource allocation |
| **Tag Distribution** | Bar chart: Medical, Evacuation, etc. | Specialist dispatch |
| **Priority Queue** | List sorted by sentiment score | Who to call first |
| **Trend Sparkline** | 4-week sentiment history | Is situation worsening? |
| **FloodNet Map** | Interactive sensor locations | Geographic targeting |

### Key Feature: Audio Playback

**Critical for Quality Assurance:**
- Liaison can click to play original recording
- Verify AI classification matches reality
- Captures context that text alone cannot (tone, crying, confusion)

> **📝 SPEAKER NOTES:**
> - For researchers: emphasize the dashboard design supports rapid decision-making
> - Walk through each component: "Urgency breakdown tells responders where to allocate resources"
> - Audio playback is the "escape hatch" from AI limitations—humans can verify
> - "When AI hears crying or panic, it scores high—but the liaison can always listen to confirm"
> - This is where qual meets quant: the numbers are on screen, but the voice is one click away
> - Transition: "So how do we know this actually works? Let's talk evaluation..."

---

# SLIDE 6: EVALUATION & IMPROVEMENT (1 minute)

## How We Measure Success

### Current Evaluation Metrics

| Metric | Target | Method |
|--------|--------|--------|
| **AI Classification Accuracy** | 90% | Human review of transcripts vs. AI tags |
| **Call Connection Rate** | 95% | Automated Vapi logging |
| **Time-to-Dashboard** | <10 sec | Webhook latency monitoring |
| **False Positive Rate** | <10% | Liaison feedback ("Override" button) |

### Continuous Improvement Approaches

**1. Human-in-the-Loop Feedback**
- Liaisons can override AI classification
- Corrections improve prompt engineering

**2. A/B Testing AI Prompts**
- Test different Gemini scoring prompts
- Measure inter-rater reliability (AI vs. human)

**3. Multi-Language Expansion**
- Currently: English only
- Next phase: Spanish voice agent

**4. Voice Tone Analysis (Future)**
- Analyze pitch, tremor, crying detection

> **📝 SPEAKER NOTES:**
> - This slide resonates with researchers—concrete metrics they can evaluate
> - 90% accuracy target is ambitious but achievable with prompt tuning
> - Human-in-the-loop is critical: "We don't trust AI blindly—liaisons can always override"
> - Mention A/B testing for credibility: "We're treating this like a research study"
> - Spanish is the #1 requested language from CBOs
> - Voice tone analysis is the "next frontier"—beyond text to audio features
> - Transition: "To get there, we need partners. Let me show you who we're working with and who we need..."

---

# SLIDE 7: PARTNERSHIPS & SUSTAINABILITY (1 minute)

## What We Need to Scale

### Current Partners

| Partner | Role | Status |
|---------|------|--------|
| **Vapi.ai** | Voice AI platform | ✅ Active |
| **FloodNet NYC** | Real-time sensor data | ✅ Active |
| **Supabase** | Database & real-time | ✅ Active |

### Required Partnerships

| Partner | Role | Status |
|---------|------|--------|
| **NYC Emergency Management** | 911 integration | 🔄 In Discussion |
| **CBOs (50 target)** | Community access | 🔄 Recruiting |
| **NYC Dept for Aging** | Senior center access | Needed |

### Resource Requirements

**Pilot Phase (500 residents):** ~$5,000/month
**Citywide Scale (60,000 residents):** ~$250,000/year
**Potential Funding:** FEMA Hazard Mitigation, NYC Emergency Management grants

> **📝 SPEAKER NOTES:**
> - Quickly highlight current partners: "We've already integrated FloodNet data and have Vapi working"
> - The gaps are clear: we need NYC EM for legitimacy and CBOs for community access
> - The pilot cost is modest—emphasize ROI: "$5K/month to potentially save lives"
> - FEMA Hazard Mitigation grants are a real funding path we're pursuing
> - Transition: "Let me close with the transformation we're trying to achieve..."

---

# SLIDE 8: CONCLUSION (30 seconds)

## The Transformation

| Before FloodVoice | After FloodVoice |
|-------------------|------------------|
| Vulnerable residents invisible | Every resident has a voice |
| 10,000 undifferentiated calls | AI-structured priority queue |
| Qualitative narratives lost | Quantified, tagged, actionable |
| Responders overwhelmed | Focus on life-threatening first |

## Our Ask

1. **Validate** our evaluation framework with PRI's expertise
2. **Connect us** with NYC Emergency Management and DOHMH
3. **Collaborate** on pilot study design

> **📝 SPEAKER NOTES:**
> - Read the table slowly—this is the "before and after" story
> - The 3 asks are specific and actionable—not vague
> - Make eye contact when saying "we need YOUR help"
> - End with the tagline: pause, then say "Because every voice matters in an emergency"
> - Let it land. Don't rush to Q&A.

---

## CONTACT

**Team:** Jessenia, Ethan, Erica, Josue, Kelvin, Shanell
**Email:** erica.ro@pursuit.org
**Repository:** github.com/Josuevillalona/flood-voice

---

*FloodVoice: Because every voice matters in an emergency.*
