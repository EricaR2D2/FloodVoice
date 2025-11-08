# FloodVoice - Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** November 8, 2025  
**Demo Date:** December 9, 2025  
**Author:** Erica Rodriguez  
**Organization:** NYC Pandemic Response Institute Data Team

---

## 1. Executive Summary

### 1.1 Product Vision
FloodVoice is a community-centered flood emergency response platform that empowers community representatives to check on vulnerable residents during flood events using SMS and automated voice calls. By combining real-time environmental monitoring data from NYC FloodNet sensors with ground-level community narratives, FloodVoice uses natural language processing (NLP) to construct dashboards that display both metrics and personal stories, enabling real-time situational awareness and more human-centered response planning.

### 1.2 Problem Statement
During flood emergencies in NYC:
- **Vulnerable populations** (elderly, disabled, non-English speakers) are often isolated and unreachable
- **Community representatives** lack real-time tools to coordinate wellness checks
- **Emergency responders** miss critical ground-level context from affected communities
- **Environmental data** (sensor readings) exists in isolation from human impact stories
- **Response planning** is reactive rather than proactive, missing early warning signals

### 1.3 Solution Overview
FloodVoice bridges the gap between **environmental data** (FloodNet sensors) and **human narratives** (community reports, social media) to create a unified situational awareness dashboard that:
1. **Monitors** real-time flood sensor data from https://dataviz.floodnet.nyc/
2. **Correlates** sensor readings with community reports and social media narratives
3. **Identifies** vulnerable populations using NYC Flood Vulnerability Index (FVI)
4. **Triggers** automated wellness check campaigns via SMS/voice calls (partner integration)
5. **Visualizes** both quantitative metrics and qualitative narratives in a unified dashboard

### 1.4 Success Metrics
- **Response Time**: Reduce time from flood detection to wellness check initiation by 70%
- **Coverage**: Enable wellness checks for 500+ vulnerable residents per flood event
- **Correlation Accuracy**: 85%+ match rate between sensor data and community reports
- **User Adoption**: 10+ community organizations using platform within 3 months
- **Demo Impact**: Secure funding/partnership commitment from NYC PRI Data Team by Dec 9

---

## 2. Target Users & Stakeholders

### 2.1 Primary Users
1. **Community Health Workers (CHWs)**
   - Need: Real-time flood alerts for their service areas
   - Use Case: Initiate wellness checks when flooding detected in vulnerable neighborhoods
   - Pain Point: Currently rely on news reports and manual neighborhood checks

2. **Community-Based Organizations (CBOs)**
   - Need: Coordinate multi-neighborhood response during flood events
   - Use Case: Deploy resources based on real-time flood severity + vulnerability data
   - Pain Point: Lack centralized view of flood impact across service areas

3. **Emergency Response Coordinators**
   - Need: Ground-level situational awareness during flood events
   - Use Case: Prioritize response based on sensor data + community narratives
   - Pain Point: Official data misses human impact stories and local context

### 2.2 Secondary Stakeholders
- **NYC Pandemic Response Institute**: Funding and institutional support
- **NYC FloodNet**: Data provider and technical partner
- **Vulnerable Residents**: Beneficiaries of wellness check system
- **Partner Developer**: Building automated calling system (integration point)

---

## 3. Core Features & Requirements

### 3.1 Real-Time Flood Monitoring Dashboard

#### 3.1.1 FloodNet Sensor Integration
**Priority:** P0 (Must Have for Demo)

**Requirements:**
- Pull real-time sensor data from https://dataviz.floodnet.nyc/ API
- Display sensor locations on interactive NYC map
- Show current flood depth readings (inches) for each sensor
- Color-code sensors by flood severity:
  - 🟢 Green: <2 inches (normal)
  - 🟡 Yellow: 2-6 inches (minor flooding)
  - 🟠 Orange: 6-12 inches (moderate flooding)
  - 🔴 Red: >12 inches (major flooding)
- Auto-refresh every 5 minutes during active flood events
- Historical trend view (last 24 hours) for each sensor

**Technical Specifications:**
- API Endpoint: FloodNet public API (to be confirmed)
- Update Frequency: 5-minute intervals
- Data Storage: SQLite database with 30-day retention
- Map Library: Leaflet.js with NYC basemap

#### 3.1.2 Flood Vulnerability Index (FVI) Overlay
**Priority:** P0 (Must Have for Demo)

**Requirements:**
- Display NYC DOHMH Flood Vulnerability Index by ZIP code
- Show vulnerability categories: LOW, MODERATE, HIGH
- Overlay FVI zones on flood sensor map
- Highlight high-vulnerability areas with active flooding
- Filter view by vulnerability level

**Data Source:**
- NYC Open Data: Flood Vulnerability Index (FVI) dataset
- FEMA flood risk zones (100-year, 500-year floodplains)

#### 3.1.3 Community Narrative Integration
**Priority:** P0 (Must Have for Demo)

**Requirements:**
- Ingest social media posts mentioning flooding (Twitter/X, Facebook, Nextdoor)
- Use NLP to extract:
  - Location (neighborhood, street, landmark)
  - Flood severity indicators (keywords: "waist-deep", "car flooded", "basement")
  - Urgency level (HIGH, MODERATE, LOW)
  - Sentiment (fear, frustration, help requests)
- Display community reports as map markers
- Correlate reports with nearby FloodNet sensors
- Show "Narrative-to-Numbers" correlation strength:
  - 🟢 Strong: Report within 0.5 miles of sensor showing flooding
  - 🟡 Moderate: Report within 1 mile of sensor
  - 🔴 Poor: No nearby sensor data

**NLP Pipeline:**
- Text processing: spaCy or NLTK for location extraction
- Sentiment analysis: TextBlob or VADER
- Urgency scoring: Custom keyword-based algorithm
- Geocoding: NYC GeoClient API for address resolution

### 3.2 Wellness Check Trigger System

#### 3.2.1 Automated Alert Generation
**Priority:** P1 (Should Have for Demo)

**Requirements:**
- Automatically detect flood events when:
  - FloodNet sensor reads >6 inches for 15+ minutes
  - Multiple community reports from same area within 1 hour
  - High-vulnerability ZIP code shows flooding
- Generate alert with:
  - Affected area (ZIP code, neighborhood)
  - Flood severity level
  - Number of vulnerable residents in area (from FVI data)
  - Recommended action (initiate wellness checks)
- Send alert to dashboard and partner calling system API

**Alert Thresholds (Configurable):**
- Minor Flood: 2-6 inches, 1+ community reports
- Moderate Flood: 6-12 inches, 3+ community reports
- Major Flood: >12 inches, 5+ community reports

#### 3.2.2 Partner API Integration
**Priority:** P1 (Should Have for Demo)

**Requirements:**
- Provide REST API endpoint for partner calling system
- API returns:
  - List of vulnerable residents in affected area
  - Contact information (phone numbers)
  - Preferred language
  - Special needs flags (mobility, medical)
- Webhook to receive call results from partner system
- Display call status on dashboard (pending, completed, no answer, needs follow-up)

**API Specification:**
```json
POST /api/trigger-wellness-checks
{
  "flood_event_id": "flood_2025_11_08_001",
  "affected_zipcodes": ["11101", "11102"],
  "severity": "moderate",
  "sensor_readings": [
    {"sensor_id": "FN001", "depth_inches": 8.5, "location": "Queens Plaza"}
  ],
  "estimated_affected_residents": 250
}

Response:
{
  "campaign_id": "wc_2025_11_08_001",
  "residents_to_contact": 250,
  "calls_initiated": 250,
  "status": "in_progress"
}
```

### 3.3 Dashboard Visualization

#### 3.3.1 Main Dashboard View
**Priority:** P0 (Must Have for Demo)

**Components:**
1. **Live Map** (60% of screen)
   - FloodNet sensors with real-time readings
   - Community report markers
   - FVI vulnerability zones (choropleth overlay)
   - FEMA flood zones (toggle layer)

2. **Metrics Panel** (top bar)
   - Active flood sensors: X/Y sensors detecting flooding
   - Community reports (last 24h): X reports
   - Vulnerable residents in affected areas: X people
   - Active wellness check campaigns: X campaigns

3. **Correlation Feed** (right sidebar)
   - List of sensor-report correlations
   - Each item shows:
     - Community report text (truncated)
     - Nearby sensor reading
     - Correlation strength
     - Time posted
   - Click to expand full details

4. **AI Insights Panel** (bottom)
   - Auto-generated insights using GPT-3.5-turbo:
     - "3 sensors in Astoria showing moderate flooding"
     - "Community reports indicate basement flooding in LIC"
     - "High-vulnerability area 11101 experiencing flooding"
   - Recommended actions

#### 3.3.2 Historical Analysis View
**Priority:** P2 (Nice to Have)

**Requirements:**
- View past flood events (last 30 days)
- Compare sensor data vs. community reports over time
- Analyze correlation accuracy
- Export data for research/reporting

---

## 4. Technical Architecture

### 4.1 Technology Stack

**Backend:**
- **Framework:** Flask (Python 3.10+)
- **Database:** SQLite (development), PostgreSQL (production)
- **Real-time Updates:** Flask-SocketIO (WebSockets)
- **API Integration:** requests library for FloodNet API
- **NLP:** spaCy, TextBlob, OpenAI GPT-3.5-turbo (via OpenRouter)

**Frontend:**
- **UI Framework:** Bootstrap 5
- **Mapping:** Leaflet.js with NYC basemap
- **Charts:** Chart.js
- **Real-time:** Socket.IO client

**Data Sources:**
- FloodNet API: https://dataviz.floodnet.nyc/
- NYC Open Data: FVI, FEMA flood zones
- Social Media: Twitter API, mock data for demo

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FloodVoice Dashboard                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Live Map    │  │  Metrics     │  │ Correlations │      │
│  │  (Leaflet)   │  │  Panel       │  │  Feed        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ WebSocket (real-time updates)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend (app.py)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ FloodNet     │  │ NLP Engine   │  │ Alert        │      │
│  │ Poller       │  │ (spaCy/GPT)  │  │ Generator    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│  FloodNet    │  │ Social Media │  │ Partner Calling API  │
│  API         │  │ Data         │  │ (Webhook)            │
└──────────────┘  └──────────────┘  └──────────────────────┘
```

### 4.3 Database Schema

**Tables:**
1. `flood_sensors` - FloodNet sensor locations and metadata
2. `sensor_readings` - Time-series flood depth data
3. `community_reports` - Social media posts and narratives
4. `fvi_zones` - Flood Vulnerability Index by ZIP code
5. `flood_events` - Detected flood events
6. `wellness_campaigns` - Triggered wellness check campaigns
7. `correlations` - Sensor-report correlation records

---

## 5. Development Roadmap

### Phase 1: Foundation (Nov 8-15) - Week 1
- ✅ Set up new GitHub repository
- ✅ Refactor codebase (remove health surveillance)
- ✅ FloodNet API integration
- ✅ Basic map visualization
- ✅ FVI data ingestion

### Phase 2: Core Features (Nov 16-23) - Week 2
- ✅ Social media narrative ingestion
- ✅ NLP pipeline for location/sentiment extraction
- ✅ Sensor-report correlation algorithm
- ✅ Real-time dashboard updates (WebSocket)

### Phase 3: Intelligence (Nov 24-30) - Week 3
- ✅ AI insights generation (GPT integration)
- ✅ Alert generation system
- ✅ Partner API development
- ✅ Historical analysis view

### Phase 4: Polish & Demo Prep (Dec 1-8) - Week 4
- ✅ UI/UX refinement
- ✅ Demo data preparation
- ✅ Testing and bug fixes
- ✅ Demo script and presentation
- ✅ Documentation

### Demo Day: December 9, 2025
- 🎯 Present to NYC PRI Data Team
- 🎯 Live demo with real FloodNet data
- 🎯 Show partner integration capability

---

## 6. Demo Scenario

### 6.1 Demo Narrative
**"From Narrative to Numbers: Community-Centered Flood Response"**

**Setup:**
- Simulated flood event in Astoria, Queens (high FVI area)
- FloodNet sensors showing rising water levels
- Social media posts from residents reporting flooding

**Demo Flow:**
1. **Show baseline** - Normal conditions, all sensors green
2. **Trigger flood event** - Sensor readings spike to 8+ inches
3. **Community reports appear** - Social media posts correlate with sensor data
4. **AI generates insights** - "Moderate flooding detected in high-vulnerability area"
5. **Alert triggers** - System recommends wellness checks for 250 residents
6. **Partner API called** - Show API request/response
7. **Dashboard updates** - Real-time correlation feed and metrics

### 6.2 Key Demo Talking Points
- **Narrative-to-Numbers**: Show how community stories validate sensor data
- **Equity Focus**: Highlight vulnerable population prioritization
- **Real-time Response**: Demonstrate speed from detection to action
- **Human-Centered**: Emphasize community voices in emergency response
- **Scalability**: Discuss expansion to other NYC neighborhoods

---

## 7. Success Criteria

### 7.1 Demo Success
- ✅ Live FloodNet data integration working
- ✅ Correlation algorithm shows 80%+ accuracy
- ✅ Dashboard loads in <3 seconds
- ✅ Real-time updates visible during demo
- ✅ Partner API successfully triggered
- ✅ Positive feedback from NYC PRI Data Team

### 7.2 Post-Demo Goals
- Secure funding for full development
- Onboard 3+ community organizations for pilot
- Establish formal partnership with NYC FloodNet
- Integrate with partner calling system
- Expand to all NYC flood-prone neighborhoods

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| FloodNet API unavailable | High | Medium | Build mock data fallback for demo |
| Social media API rate limits | Medium | High | Use pre-collected demo dataset |
| Partner integration delays | Medium | Medium | Build standalone demo mode |
| NLP accuracy issues | Medium | Medium | Manual curation of demo narratives |
| Demo technical failure | High | Low | Pre-record backup video demo |

---

## 9. Future Enhancements (Post-Demo)

### 9.1 Phase 2 Features
- Multi-language support (Spanish, Chinese, Bengali)
- Mobile app for community health workers
- SMS-based resident reporting
- Integration with 311 flood reports
- Predictive flood modeling (ML-based)

### 9.2 Expansion Opportunities
- Adapt for other climate emergencies (heat waves, hurricanes)
- Expand to other cities with FloodNet deployments
- Partner with FEMA for national deployment
- Research publication on Narrative-to-Numbers methodology

---

## 10. Appendices

### 10.1 Data Sources
- **FloodNet**: https://dataviz.floodnet.nyc/
- **NYC FVI**: https://data.cityofnewyork.us/Health/Flood-Vulnerability-Index-FVI-/qrqj-xeaq
- **FEMA Flood Zones**: https://msc.fema.gov/portal/home

### 10.2 Key Contacts
- **NYC PRI Data Team**: Demo audience (Dec 9)
- **Partner Developer**: Calling system integration
- **FloodNet Team**: Data access and technical support

### 10.3 References
- NYC FloodNet Documentation
- NYC DOHMH Flood Vulnerability Index Methodology
- FEMA Flood Risk Assessment Guidelines

---

**Document Status:** Draft v1.0  
**Next Review:** November 15, 2025  
**Approval Required:** NYC PRI Data Team Lead

