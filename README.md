# 🌊 FloodVoice - Community-Centered Flood Emergency Response Platform

**Empowering community representatives to check on vulnerable residents during flood events using real-time data and AI-powered insights.**

## 🎯 Vision

FloodVoice bridges the gap between environmental monitoring data and human narratives by combining real-time FloodNet sensor readings with ground-level community reports. Using natural language processing (NLP), we transform community voices into actionable emergency response data, enabling more human-centered and equitable flood response planning.

## ✨ Key Features

### 1. Real-Time Flood Monitoring
- **FloodNet Integration**: Live sensor data from https://dataviz.floodnet.nyc/
- **Interactive Map**: Visualize flood conditions across NYC neighborhoods
- **Automated Alerts**: Instant notifications when flooding is detected

### 2. Community Narrative Integration
- **Social Media Monitoring**: Track flood-related posts from affected communities
- **NLP Processing**: Extract location, urgency, and sentiment from narratives
- **Correlation Engine**: Match community reports with nearby sensor readings

### 3. Vulnerability-Focused Response
- **NYC Flood Vulnerability Index (FVI)**: Identify high-risk populations
- **FEMA Flood Zones**: Overlay official risk assessments
- **Targeted Wellness Checks**: Prioritize vulnerable residents for outreach

### 4. Partner Integration
- **Wellness Check API**: Trigger automated SMS/voice calls to vulnerable residents
- **Real-time Status**: Track campaign progress and resident responses
- **Collaborative Response**: Coordinate with community organizations

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EricaR2D2/FloodVoice.git
   cd FloodVoice
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Load demo data**
   ```bash
   python demo_flood_posts_generator.py
   python fema_flood_data_ingestion.py
   python nyc_fvi_data_ingestion.py
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   - Open your browser to http://localhost:5000
   - View real-time flood monitoring and community reports

## 📊 Dashboard Overview

### Main Dashboard
- **Live Map**: FloodNet sensors, community reports, vulnerability zones
- **Metrics Panel**: Active sensors, community reports, flooding detected
- **Correlation Feed**: Real-time matching of reports with sensor data
- **AI Insights**: Automated analysis and recommended actions

### Historical Analysis
- View past flood events
- Analyze correlation accuracy
- Export data for research

## 🔧 Configuration

### API Keys Required

1. **FloodNet API** (for sensor data)
   - Get access from https://dataviz.floodnet.nyc/
   - Add to `.env`: `FLOODNET_API_KEY=your_key`

2. **OpenRouter API** (for AI insights)
   - Get key from https://openrouter.ai/
   - Add to `.env`: `OPENROUTER_API_KEY=your_key`

3. **NYC GeoClient API** (for geocoding)
   - Get credentials from https://developer.cityofnewyork.us/
   - Add to `.env`: `NYC_GEOCLIENT_APP_ID` and `NYC_GEOCLIENT_APP_KEY`

### Alert Thresholds

Configure flood severity thresholds in `.env`:
```
MINOR_FLOOD_THRESHOLD=2.0      # inches
MODERATE_FLOOD_THRESHOLD=6.0   # inches
MAJOR_FLOOD_THRESHOLD=12.0     # inches
```

## 📁 Project Structure

```
FloodVoice/
├── app.py                              # Main Flask application
├── config.py                           # Configuration management
├── flood_dashboard.py                  # Flood data processing logic
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── README.md                           # This file
├── FLOODVOICE_PRD.md                  # Product Requirements Document
├── FLOODVOICE_BUILD_PLAN.md           # Development roadmap
├── fema_flood_data_ingestion.py       # FEMA flood zone data loader
├── nyc_fvi_data_ingestion.py          # NYC Flood Vulnerability Index loader
├── social_media_narrative_integration.py  # Social media data processor
├── demo_flood_posts_generator.py      # Demo data generator
├── templates/                          # HTML templates
│   └── flood_dashboard.html           # Main dashboard UI
├── static/                             # Static assets
│   ├── css/                           # Stylesheets
│   ├── js/                            # JavaScript files
│   └── geojson/                       # NYC boundaries, flood zones
├── fema_data/                          # FEMA flood zone data
├── fvi_data/                           # NYC FVI data
└── social_media_data/                  # Community reports data
```

## 🧪 Demo Mode

FloodVoice includes a demo mode with realistic simulated data:

1. **Generate demo flood posts**
   ```bash
   python demo_flood_posts_generator.py
   ```

2. **Enable demo mode in `.env`**
   ```
   DEMO_MODE=True
   USE_MOCK_DATA=True
   ```

3. **Run the application**
   - Dashboard will show simulated flood event in Astoria, Queens
   - Community reports correlate with sensor readings
   - AI generates insights based on demo scenario

## 🔌 Partner API

FloodVoice provides a REST API for partner calling systems:

### Trigger Wellness Checks
```bash
POST /api/trigger-wellness-checks
Content-Type: application/json

{
  "flood_event_id": "flood_2025_11_08_001",
  "affected_zipcodes": ["11101", "11102"],
  "severity": "moderate"
}
```

### Receive Call Results
```bash
POST /api/wellness-check-result
Content-Type: application/json

{
  "campaign_id": "wc_2025_11_08_001",
  "resident_id": "12345",
  "status": "completed",
  "notes": "Resident is safe, no assistance needed"
}
```

## 📈 Success Metrics

- **Response Time**: Reduce time from flood detection to wellness check initiation by 70%
- **Coverage**: Enable wellness checks for 500+ vulnerable residents per flood event
- **Correlation Accuracy**: 85%+ match rate between sensor data and community reports
- **User Adoption**: 10+ community organizations using platform within 3 months

## 🤝 Contributing

We welcome contributions from the community! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is developed for the NYC Pandemic Response Institute Data Team.

## 📞 Contact

**Developer**: Erica Rodriguez  
**Email**: erica.ro@pursuit.org  
**Organization**: NYC Pandemic Response Institute

## 🙏 Acknowledgments

- **NYC FloodNet**: Real-time flood sensor data
- **NYC DOHMH**: Flood Vulnerability Index data
- **FEMA**: Flood risk zone data
- **NYC Pandemic Response Institute**: Project support and funding

---

**Built with ❤️ for vulnerable communities facing climate emergencies.**

**Demo Date**: December 9, 2025 | NYC Pandemic Response Institute Data Team Meeting

