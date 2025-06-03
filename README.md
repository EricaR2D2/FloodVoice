# Public Health MVP Dashboard

A comprehensive public health data analysis platform for NYC Center for Population Health Data Science analysts, featuring unified data visualization, AI-powered pattern detection, and real-time alerting.

## 🎯 Value Proposition

**For data analysts at the NYC Center for Population Health Data Science**, this solution provides **faster and earlier detection of public health risks** by unifying siloed datasets and using transparent AI to flag emerging patterns, **unlike manual querying and siloed dashboards**, which delay insights and limit cross-system visibility.

## ✨ Key Features

### 1. Unified Data Dashboard with Real-Time Feeds
- **Multi-source integration**: Hospital, NYC COVID, CDC ILI, Air Quality data
- **Real-time visualization**: Live charts and metrics
- **Cross-system visibility**: Single interface for all data sources

### 2. Explainable AI Pattern Alerts
- **Transparent AI**: Natural language explanations for all detected patterns
- **Context-rich analysis**: Integrates environmental and health data
- **Trust-building**: Shows methodology, confidence scores, and data sources

### 3. Customizable Risk Thresholds & Alert Management
- **Configurable detection**: Adjustable spike/drop/consistency thresholds
- **Notification preferences**: Email and Slack integration
- **Interactive settings**: Web-based configuration interface

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

3. **Run data ingestion (Phase 1)**
   ```bash
   python phase1_data_ingestion.py
   ```

4. **Run pattern detection (Phase 2)**
   ```bash
   python phase2_pattern_detection.py
   ```

5. **Start the dashboard (Phase 3)**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   - Main Dashboard: http://localhost:5000
   - Pattern Analysis: http://localhost:5000/patterns
   - Alert Settings: http://localhost:5000/settings

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
