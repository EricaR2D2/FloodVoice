# FloodVoice: From Voices to Values
## One-Page Summary | NYC PRI Meeting | December 9, 2025

---

### 🎯 The Problem

During floods, **vulnerable NYC residents are invisible** to emergency responders:
- **50,000-100,000** basement apartment residents at high risk
- **Hurricane Ida (2021):** 11 deaths in NYC, 10,000+ calls/hour overwhelmed 911
- Text-based alerts fail to reach elderly, non-English speakers, and residents with disabilities

**Core Challenge:** Emergency responders cannot distinguish life-threatening calls from non-urgent ones when overwhelmed with undifferentiated qualitative data.

---

### 💡 The Solution: FloodVoice

**One-Line Description:**  
An AI-powered voice-based welfare check system that converts thousands of qualitative phone conversations into a structured, prioritized emergency response dataset in real-time.

**How It Works:**
```
FloodNet Sensors → Telegram Alert → AI Voice Calls → Gemini NLP Analysis → Priority Dashboard
   (>4" depth)       to Liaisons      to Residents     Sentiment + Tags      for Responders
```

**Three Key Innovations:**
1. **Zero-Friction Access** — Works with any phone (landline or cell)
2. **Massive Scale** — 1 liaison can check 500 residents in 60 seconds
3. **Narrative-to-Numbers** — AI extracts sentiment, urgency, and needs from natural speech

---

### 📊 Data Transformation (Qualitative → Quantitative)

| Data Type | Source | Classification |
|-----------|--------|----------------|
| Audio recordings | Voice calls | **Qualitative** |
| Transcripts | Speech-to-text | **Qualitative** |
| Sentiment scores (1-10) | Gemini AI | Quantitative |
| Need tags (7 categories) | Gemini AI | Quantitative |

**Example Transformation:**

*Input:* "I'm okay, but the water is coming into my basement. About ankle-deep now."

*Output:* `{ sentiment_score: 4, tags: ["Property Damage", "Safe"], risk: "MODERATE" }`

---

### 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Voice AI | Vapi.ai + GPT-4o-mini + ElevenLabs | Outbound calls & conversation |
| NLP Analysis | Google Gemini 2.5 | Sentiment scoring & tagging |
| Database | Supabase (PostgreSQL) | Real-time data & WebSocket |
| Flood Data | FloodNet NYC (50+ sensors) | Automated trigger (>4" depth) |
| Alerts | Telegram Bot API | Distress notifications |

**Fixed Taxonomy (7 Tags):** Medical, Food/Water, Power, Evacuation, Mental Health, Property Damage, Safe

---

### 📏 Evaluation Metrics

| Metric | Target | Method |
|--------|--------|--------|
| AI Classification Accuracy | **90%** | Human review vs. AI tags |
| Call Connection Rate | **95%** | Vapi logging |
| Time-to-Dashboard | **<10 sec** | Webhook latency |
| False Positive Rate | **<10%** | Liaison override feedback |

**Improvement Approaches:** Human-in-the-loop feedback, A/B prompt testing, Spanish language expansion

---

### 🤝 Partnership Status

| Partner | Status |
|---------|--------|
| Vapi.ai, FloodNet NYC, Supabase | ✅ Active |
| NYC Emergency Management | 🔄 In Discussion |
| Community-Based Organizations (50 target) | 🔄 Recruiting |

**Resource Requirements:**
- Pilot (500 residents): ~$5,000/month
- Citywide (60,000 residents): ~$250,000/year

---

### 📞 Contact & Next Steps

**Team:** Jessenia, Ethan, Erica, Josue, Kelvin, Shanell  
**Email:** erica.ro@pursuit.org  
**Repository:** github.com/Josuevillalona/flood-voice

**Our Ask:**
1. Validate our evaluation framework with PRI's data science expertise
2. Connect us with NYC Emergency Management and DOHMH
3. Collaborate on pilot study design

---

*"FloodVoice: Because every voice matters in an emergency."*

