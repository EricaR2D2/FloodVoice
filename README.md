# 🏥 Public Health MVP - Real-Time Surveillance Dashboard

A **live public health monitoring system** for NYC Center for Population Health Data Science analysts, featuring real-time data feeds, AI-powered pattern detection, and immediate alerting for current health threats.

## 🎯 Value Proposition

**For data analysts at the NYC Center for Population Health Data Science**, this solution provides **real-time detection of emerging public health threats** by continuously monitoring live NYC health data and using transparent AI to flag current patterns as they develop, **unlike static reports and delayed dashboards**, which miss critical early warning signals and limit rapid response capabilities.

## ✨ Key Features

### 1. Live Health Data Surveillance
- **Real-time NYC COVID data**: Current daily cases, hospitalizations, deaths by borough
- **Live ER monitoring**: Respiratory illness visits across NYC hospitals
- **Current data feeds**: CDC surveillance, air quality, and health indicators
- **Data freshness tracking**: Clear visibility into how current your data is

### 2. Real-Time AI Pattern Detection
- **Live pattern scanning**: Detects spikes, drops, and trends as they emerge
- **Current threat focus**: Prioritizes patterns from the last 7-14 days
- **Instant AI explanations**: Natural language insights about current health events
- **Borough-level alerts**: Geographic targeting for NYC's 5 boroughs

### 3. Immediate Alert Management & Response
- **Real-time notifications**: Instant alerts when patterns are detected
- **Current risk thresholds**: Configurable detection for live surveillance
- **Live dashboard updates**: Automatic refresh of current health status

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EricaR2D2/PublicHealthMVP.git
   cd PublicHealthMVP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Load real-time data (Phase 1)**
   ```bash
   python phase1_data_ingestion.py
   ```
   *Fetches current NYC COVID data, generates hospital ER data, and sets up real-time feeds*

4. **Initialize pattern detection (Phase 2)**
   ```bash
   python phase2_pattern_detection.py
   ```
   *Sets up real-time pattern scanning and AI analysis capabilities*

5. **Start live surveillance dashboard (Phase 3)**
   ```bash
   python app.py
   ```
   *Launches the real-time monitoring interface with live updates*

6. **Access the live dashboard**
   - **Real-Time Dashboard**: http://localhost:5000 - Live health surveillance
   - **Current Patterns**: http://localhost:5000/patterns - Active alerts and analysis
   - **Alert Settings**: http://localhost:5000/settings - Configure real-time thresholds

## 📊 Dashboard Features

### Main Dashboard
- **Summary metrics**: Total records, patterns detected, data freshness
- **Time series charts**: ER respiratory visits over time
- **Pattern distribution**: Visual breakdown of alert types
- **Recent alerts**: Latest pattern detections with AI explanations

### Pattern Analysis
- **Advanced filtering**: By type, location, date range, confidence
- **Detailed view**: Full AI explanations and context data
- **Statistics**: Pattern counts and confidence metrics
- **Export capabilities**: CSV download of filtered results

### Alert Settings
- **Threshold configuration**: Spike (30%), Drop (30%), Consistently High (20%)
- **Notification setup**: Email and Slack preferences
- **Test functions**: Validate settings and data connectivity

## 🔧 Configuration

### Pattern Detection Thresholds
- **Spike Threshold**: 30% above 7-day average (configurable)
- **Drop Threshold**: 30% below 7-day average (configurable)
- **Consistently High**: 20% above average for 3+ days (configurable)

### Data Sources
- **Hospital Data**: ER respiratory visits by ZIP code
- **NYC COVID Data**: Daily cases, hospitalizations, deaths
- **CDC ILI Data**: Influenza-like illness percentages
- **Air Quality Data**: AQI, PM2.5, ozone levels

### AI Integration
- **Model**: GPT-3.5-turbo via OpenRouter API
- **Explanations**: Context-aware natural language analysis
- **Transparency**: Shows data sources and reasoning

## 📁 Project Structure

```
PublicHealthMVP/
├── phase1_data_ingestion.py      # Data collection and cleaning
├── phase2_pattern_detection.py   # AI pattern analysis
├── app.py                        # Flask web application
├── templates/                    # HTML templates
│   ├── base.html                # Base template with navigation
│   ├── dashboard.html           # Main dashboard
│   ├── patterns.html            # Pattern analysis page
│   └── settings.html            # Configuration page
├── public_health_data.db         # SQLite database
├── pattern_analysis_results.csv  # Pattern detection results
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🧪 Testing & Validation

### Automated Testing
```bash
python test_phase2_validation.py
```

### Manual Testing
1. **Data Ingestion**: Verify all data sources load successfully
2. **Pattern Detection**: Confirm patterns are detected and explained
3. **Dashboard**: Check all visualizations and real-time updates
4. **Settings**: Test threshold changes and notifications

## 🔮 Future Enhancements

### Phase 4: Advanced Analytics
- **Predictive modeling**: Forecast future health risks
- **Scenario simulation**: "What-if" analysis capabilities
- **Machine learning**: Automated threshold optimization
- **Integration APIs**: Connect to external health systems

### Production Deployment
- **Scalability**: Multi-user support and load balancing
- **Security**: Authentication and authorization
- **Monitoring**: System health and performance metrics
- **Backup**: Automated data backup and recovery

## 📈 Success Metrics

### Measurable Outcomes
- **Time-to-detection**: 50% reduction in pattern identification time
- **Data access**: Single interface vs. multiple system logins
- **Alert accuracy**: <10% false positive rate
- **User adoption**: Trust scores and usage analytics

### Key Performance Indicators
- **Pattern detection accuracy**: 95%+ true positive rate
- **Response time**: <30 seconds for dashboard updates
- **Data freshness**: Real-time to 5-minute delays
- **System uptime**: 99.9% availability target

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is developed for the NYC Center for Population Health Data Science.

## 📞 Support

For questions or support, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for public health analysts who deserve better tools.**
