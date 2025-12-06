# FloodVoice - Detailed Build Plan

**Project:** FloodVoice - Community-Centered Flood Emergency Response Platform  
**Timeline:** November 8 - December 9, 2025 (31 days)  
**Demo Date:** December 9, 2025  
**Developer:** Erica Rowe-Owen, Kelvin Saldana, Ethan Davey, Josue Villalona, Shanell Holback, Jessenia Cintron

---

## 📅 Timeline Overview

```
Week 1 (Nov 8-15):  Foundation & Setup
Week 2 (Nov 16-23): Core Features & Integration
Week 3 (Nov 24-30): Intelligence & Partner API
Week 4 (Dec 1-8):   Polish, Testing & Demo Prep
Dec 9:              DEMO DAY 🎯
```

---

## 🏗️ WEEK 1: Foundation & Setup (Nov 8-15)

### Day 1-2: Repository Setup & Codebase Refactoring (Nov 8-9)

**Goal:** Clean slate for FloodVoice-focused development

**Tasks:**
- [x] Create FLOODVOICE_PRD.md
- [ ] Create FLOODVOICE_BUILD_PLAN.md
- [ ] Set up Git remote for https://github.com/EricaR2D2/FloodVoice.git
- [ ] Create new folder structure:
  ```
  FloodVoice/
  ├── app.py                    # Main Flask app (flood-focused)
  ├── config.py                 # Configuration management
  ├── requirements.txt          # Dependencies
  ├── README.md                 # FloodVoice-specific README
  ├── data/                     # Data ingestion scripts
  │   ├── floodnet_poller.py   # FloodNet API integration
  │   ├── fvi_ingestion.py     # FVI data loader
  │   ├── social_media.py      # Social media ingestion
  │   └── fema_zones.py        # FEMA flood zones
  ├── models/                   # Database models
  │   ├── __init__.py
  │   ├── sensor.py            # FloodNet sensors
  │   ├── report.py            # Community reports
  │   └── event.py             # Flood events
  ├── services/                 # Business logic
  │   ├── __init__.py
  │   ├── correlation.py       # Sensor-report correlation
  │   ├── nlp_engine.py        # NLP processing
  │   └── alert_generator.py   # Alert system
  ├── api/                      # REST API endpoints
  │   ├── __init__.py
  │   ├── flood_data.py        # Flood data endpoints
  │   └── partner_api.py       # Partner integration
  ├── templates/                # HTML templates
  │   ├── base.html
  │   ├── dashboard.html       # Main flood dashboard
  │   └── historical.html      # Historical analysis
  ├── static/                   # Static assets
  │   ├── css/
  │   ├── js/
  │   └── geojson/             # NYC boundaries, flood zones
  └── tests/                    # Unit tests
  ```
- [ ] Remove health surveillance files:
  - Delete: `phase2_pattern_detection.py`, `forecasting_engine.py`
  - Delete: `templates/patterns.html`, `templates/settings.html`
  - Delete: COVID/hospital data ingestion scripts
  - Keep: `flood_dashboard.py`, `fema_flood_data_ingestion.py`, `nyc_fvi_data_ingestion.py`
- [ ] Update `requirements.txt` with FloodVoice dependencies:
  ```
  Flask==2.3.0
  Flask-SocketIO==5.3.0
  Flask-CORS==4.0.0
  requests==2.31.0
  pandas==2.0.0
  geopandas==0.13.0
  folium==0.14.0
  spacy==3.5.0
  textblob==0.17.1
  openai==1.0.0
  python-dotenv==1.0.0
  ```
- [ ] Create `.env.example` for API keys
- [ ] Initial commit and push to new repo

**Deliverable:** Clean FloodVoice repository with organized structure

---

### Day 3-4: FloodNet API Integration (Nov 10-11)

**Goal:** Real-time flood sensor data ingestion

**Tasks:**
- [ ] Research FloodNet API documentation
  - Endpoint: https://dataviz.floodnet.nyc/ (check for public API)
  - Alternative: Web scraping if no public API
  - Fallback: Mock data generator for demo
- [ ] Create `data/floodnet_poller.py`:
  ```python
  class FloodNetPoller:
      def __init__(self, api_key=None):
          self.api_url = "https://api.floodnet.nyc/sensors"  # TBD
          self.update_interval = 300  # 5 minutes
      
      def fetch_sensor_data(self):
          """Fetch current readings from all sensors"""
          pass
      
      def get_sensor_locations(self):
          """Get sensor metadata (lat/lon, ID, name)"""
          pass
      
      def poll_continuously(self):
          """Background task to poll API every 5 minutes"""
          pass
  ```
- [ ] Create database schema for sensors:
  ```sql
  CREATE TABLE flood_sensors (
      sensor_id TEXT PRIMARY KEY,
      name TEXT,
      latitude REAL,
      longitude REAL,
      borough TEXT,
      neighborhood TEXT,
      installation_date TEXT,
      status TEXT  -- active, inactive, maintenance
  );
  
  CREATE TABLE sensor_readings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sensor_id TEXT,
      timestamp TEXT,
      flood_depth_inches REAL,
      water_present BOOLEAN,
      temperature REAL,
      battery_level REAL,
      FOREIGN KEY (sensor_id) REFERENCES flood_sensors(sensor_id)
  );
  ```
- [ ] Implement data ingestion with error handling
- [ ] Create mock data generator for demo fallback:
  - 20-30 sensors across NYC
  - Realistic flood depth patterns
  - Time-series data for last 24 hours
- [ ] Test API integration and data storage
- [ ] Create admin script to view sensor status

**Deliverable:** Working FloodNet data pipeline with 5-minute updates

---

### Day 5-6: FVI & FEMA Data Integration (Nov 12-13)

**Goal:** Vulnerability and risk zone data loaded

**Tasks:**
- [ ] Refactor existing `nyc_fvi_data_ingestion.py`:
  - Clean up for FloodVoice focus
  - Add ZIP code to borough mapping
  - Calculate vulnerability scores
- [ ] Download and process FVI data:
  - Source: https://data.cityofnewyork.us/Health/Flood-Vulnerability-Index-FVI-/qrqj-xeaq
  - Fields needed: ZIP code, FVI score, vulnerability category
- [ ] Refactor `fema_flood_data_ingestion.py`:
  - Load FEMA flood zones (100-year, 500-year)
  - Convert to GeoJSON for map overlay
- [ ] Create database schema:
  ```sql
  CREATE TABLE fvi_zones (
      zipcode TEXT PRIMARY KEY,
      borough TEXT,
      fvi_score REAL,
      vulnerability_category TEXT,  -- LOW, MODERATE, HIGH
      population INTEGER,
      elderly_population INTEGER,
      disabled_population INTEGER,
      non_english_speakers INTEGER
  );
  
  CREATE TABLE fema_flood_zones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      zone_type TEXT,  -- 100-year, 500-year
      geometry TEXT,   -- GeoJSON polygon
      risk_level TEXT  -- HIGH, MODERATE, LOW
  );
  ```
- [ ] Create spatial join function to match sensors to FVI zones
- [ ] Generate summary statistics:
  - Number of sensors in high-vulnerability areas
  - Population at risk by borough
- [ ] Export processed data to `static/geojson/` for map layers

**Deliverable:** FVI and FEMA data integrated with sensor locations

---

### Day 7: Basic Dashboard & Map (Nov 14-15)

**Goal:** Functional map visualization

**Tasks:**
- [ ] Create `templates/base.html` with Bootstrap 5 layout
- [ ] Create `templates/dashboard.html`:
  - Full-screen map (Leaflet.js)
  - Top metrics bar (placeholder values)
  - Right sidebar for correlations (empty for now)
- [ ] Implement Leaflet map in `static/js/flood_map.js`:
  ```javascript
  // Initialize map centered on NYC
  const map = L.map('flood-map').setView([40.7128, -74.0060], 11);
  
  // Add basemap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Load sensor markers
  function loadSensors() {
      fetch('/api/sensors')
          .then(res => res.json())
          .then(data => {
              data.sensors.forEach(sensor => {
                  const color = getColorByDepth(sensor.flood_depth_inches);
                  L.circleMarker([sensor.lat, sensor.lon], {
                      color: color,
                      radius: 8
                  }).addTo(map).bindPopup(sensor.name);
              });
          });
  }
  ```
- [ ] Create Flask routes in `app.py`:
  ```python
  @app.route('/')
  def dashboard():
      return render_template('dashboard.html')
  
  @app.route('/api/sensors')
  def get_sensors():
      # Return current sensor data as JSON
      pass
  ```
- [ ] Add FVI choropleth layer (toggle on/off)
- [ ] Add FEMA flood zone overlay (toggle on/off)
- [ ] Test map loads with real/mock sensor data

**Deliverable:** Interactive map showing sensors and vulnerability zones

**Week 1 Milestone:** ✅ Foundation complete - data pipeline + basic map working

---

## 🚀 WEEK 2: Core Features & Integration (Nov 16-23)

### Day 8-9: Social Media Narrative Ingestion (Nov 16-17)

**Goal:** Community reports integrated into system

**Tasks:**
- [ ] Refactor `social_media_narrative_integration.py` for flood focus
- [ ] Create `data/social_media.py`:
  ```python
  class SocialMediaIngestion:
      def __init__(self):
          self.keywords = ['flood', 'flooding', 'water', 'basement flooded', 
                          'street flooded', 'subway flooded']
      
      def fetch_twitter_posts(self, hours_back=24):
          """Fetch flood-related tweets from NYC"""
          pass
      
      def extract_location(self, text):
          """Use NLP to extract location from post"""
          pass
      
      def calculate_urgency(self, text, engagement):
          """Score urgency based on keywords and engagement"""
          pass
  ```
- [ ] For demo: Use `demo_flood_posts_generator.py` to create realistic dataset
  - 50-100 posts covering different NYC neighborhoods
  - Mix of urgency levels (HIGH, MODERATE, LOW)
  - Realistic timestamps (last 24 hours)
- [ ] Create database schema:
  ```sql
  CREATE TABLE community_reports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id TEXT UNIQUE,
      text TEXT,
      source TEXT,  -- twitter, facebook, nextdoor
      post_date TEXT,
      location_raw TEXT,  -- extracted from text
      latitude REAL,
      longitude REAL,
      neighborhood TEXT,
      borough TEXT,
      urgency_level TEXT,  -- HIGH, MODERATE, LOW
      urgency_score REAL,
      sentiment_polarity REAL,
      engagement_score INTEGER,
      processed_date TEXT
  );
  ```
- [ ] Implement geocoding for location extraction:
  - Use NYC GeoClient API or Google Geocoding API
  - Fallback to neighborhood name matching
- [ ] Test ingestion with demo data

**Deliverable:** Community reports stored and geocoded

---

### Day 10-11: NLP Pipeline (Nov 18-19)

**Goal:** Intelligent text processing for narratives

**Tasks:**
- [ ] Create `services/nlp_engine.py`:
  ```python
  import spacy
  from textblob import TextBlob
  
  class NLPEngine:
      def __init__(self):
          self.nlp = spacy.load("en_core_web_sm")
          self.flood_keywords = {
              'severe': ['waist-deep', 'car flooded', 'evacuate'],
              'moderate': ['ankle-deep', 'street flooded', 'basement'],
              'minor': ['puddles', 'wet', 'damp']
          }
      
      def extract_location(self, text):
          """Extract location entities (GPE, LOC)"""
          doc = self.nlp(text)
          locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
          return locations
      
      def analyze_sentiment(self, text):
          """Get sentiment polarity and subjectivity"""
          blob = TextBlob(text)
          return blob.sentiment
      
      def calculate_urgency(self, text, engagement_score):
          """Score urgency 0-1 based on keywords and engagement"""
          severity_score = 0
          for level, keywords in self.flood_keywords.items():
              if any(kw in text.lower() for kw in keywords):
                  severity_score = {'severe': 1.0, 'moderate': 0.6, 'minor': 0.3}[level]
                  break
          
          engagement_factor = min(engagement_score / 1000, 0.3)
          return min(severity_score + engagement_factor, 1.0)
  ```
- [ ] Install spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Process all community reports through NLP pipeline
- [ ] Add AI-generated summary using GPT-3.5-turbo:
  ```python
  def generate_report_summary(self, reports):
      """Use GPT to summarize multiple flood reports"""
      prompt = f"Summarize these flood reports: {reports}"
      # Call OpenRouter API
      pass
  ```
- [ ] Test NLP accuracy on demo dataset
- [ ] Create admin dashboard to review NLP results

**Deliverable:** NLP pipeline processing community reports

---

### Day 12-13: Correlation Algorithm (Nov 20-21)

**Goal:** Match community reports with sensor data

**Tasks:**
- [ ] Create `services/correlation.py`:
  ```python
  from geopy.distance import geodesic
  
  class CorrelationEngine:
      def __init__(self):
          self.max_distance_miles = 1.0  # Reports within 1 mile of sensor
          self.time_window_hours = 2     # Reports within 2 hours of reading
      
      def correlate_reports_with_sensors(self, reports, sensor_readings):
          """Find matching sensor data for each report"""
          correlations = []
          
          for report in reports:
              nearby_sensors = self.find_nearby_sensors(
                  report['latitude'], 
                  report['longitude']
              )
              
              for sensor in nearby_sensors:
                  reading = self.get_sensor_reading_at_time(
                      sensor['sensor_id'], 
                      report['post_date']
                  )
                  
                  if reading:
                      correlation_strength = self.calculate_correlation_strength(
                          report, sensor, reading
                      )
                      
                      correlations.append({
                          'report_id': report['id'],
                          'sensor_id': sensor['sensor_id'],
                          'distance_miles': self.calculate_distance(report, sensor),
                          'time_diff_minutes': self.calculate_time_diff(report, reading),
                          'correlation_strength': correlation_strength,
                          'report_urgency': report['urgency_level'],
                          'sensor_depth': reading['flood_depth_inches']
                      })
          
          return correlations
      
      def calculate_correlation_strength(self, report, sensor, reading):
          """Score correlation 0-1 based on distance, time, severity match"""
          # Strong: close distance + recent + severity matches
          # Moderate: medium distance or time lag
          # Weak: far distance or large time gap
          pass
  ```
- [ ] Create database schema:
  ```sql
  CREATE TABLE correlations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      report_id INTEGER,
      sensor_id TEXT,
      distance_miles REAL,
      time_diff_minutes INTEGER,
      correlation_strength TEXT,  -- STRONG, MODERATE, WEAK
      correlation_score REAL,
      created_at TEXT,
      FOREIGN KEY (report_id) REFERENCES community_reports(id),
      FOREIGN KEY (sensor_id) REFERENCES flood_sensors(sensor_id)
  );
  ```
- [ ] Implement correlation algorithm
- [ ] Run correlation on demo dataset
- [ ] Validate results (aim for 80%+ strong correlations)
- [ ] Create API endpoint: `/api/correlations`

**Deliverable:** Working correlation engine matching reports to sensors

---

### Day 14: Real-Time Updates (WebSocket) (Nov 22-23)

**Goal:** Live dashboard updates without page refresh

**Tasks:**
- [ ] Set up Flask-SocketIO in `app.py`:
  ```python
  from flask_socketio import SocketIO, emit
  
  socketio = SocketIO(app, cors_allowed_origins="*")
  
  @socketio.on('connect')
  def handle_connect():
      print('Client connected')
      emit('initial_data', get_current_flood_data())
  
  def broadcast_sensor_update(sensor_data):
      """Send new sensor reading to all connected clients"""
      socketio.emit('sensor_update', sensor_data)
  ```
- [ ] Create background task to poll FloodNet API:
  ```python
  import threading
  
  def poll_floodnet_continuously():
      while True:
          new_data = floodnet_poller.fetch_sensor_data()
          broadcast_sensor_update(new_data)
          time.sleep(300)  # 5 minutes
  
  # Start background thread
  threading.Thread(target=poll_floodnet_continuously, daemon=True).start()
  ```
- [ ] Update frontend `static/js/dashboard.js`:
  ```javascript
  const socket = io();
  
  socket.on('sensor_update', function(data) {
      updateSensorMarkers(data);
      updateMetrics(data);
  });
  
  socket.on('new_correlation', function(data) {
      addCorrelationToFeed(data);
  });
  ```
- [ ] Test real-time updates with multiple browser windows
- [ ] Add loading states and error handling

**Deliverable:** Dashboard updates in real-time as new data arrives

**Week 2 Milestone:** ✅ Core features complete - NLP + correlation + real-time updates

---

## 🧠 WEEK 3: Intelligence & Partner API (Nov 24-30)

### Day 15-16: AI Insights Generation (Nov 24-25)

**Goal:** GPT-powered flood insights

**Tasks:**
- [ ] Set up OpenRouter API (GPT-3.5-turbo):
  - Get API key from https://openrouter.ai/
  - Add to `.env`: `OPENROUTER_API_KEY=your_key`
- [ ] Create `services/ai_insights.py`:
  ```python
  import openai
  
  class AIInsightsGenerator:
      def __init__(self, api_key):
          self.client = openai.OpenAI(
              base_url="https://openrouter.ai/api/v1",
              api_key=api_key
          )
      
      def generate_flood_insights(self, sensor_data, reports, correlations):
          """Generate AI insights from current flood situation"""
          prompt = f"""
          Analyze this NYC flood situation and provide 3-5 key insights:
          
          Sensor Data: {len(sensor_data)} sensors, {self.count_flooding(sensor_data)} showing flooding
          Community Reports: {len(reports)} reports in last 24h
          Correlations: {len(correlations)} strong matches between reports and sensors
          
          High-risk areas: {self.get_high_risk_areas(sensor_data, correlations)}
          
          Provide insights in this format:
          1. [Insight about flooding severity and location]
          2. [Insight about vulnerable populations affected]
          3. [Recommended actions for emergency response]
          """
          
          response = self.client.chat.completions.create(
              model="openai/gpt-3.5-turbo",
              messages=[{"role": "user", "content": prompt}]
          )
          
          return response.choices[0].message.content
  ```
- [ ] Create insights display panel in dashboard
- [ ] Generate insights every 15 minutes or when new flood event detected
- [ ] Cache insights to avoid excessive API calls
- [ ] Add manual "Regenerate Insights" button

**Deliverable:** AI-generated insights displayed on dashboard

---

### Day 17-18: Alert Generation System (Nov 26-27)

**Goal:** Automated flood event detection and alerts

**Tasks:**
- [ ] Create `services/alert_generator.py`:
  ```python
  class AlertGenerator:
      def __init__(self):
          self.thresholds = {
              'minor_flood': 2.0,      # inches
              'moderate_flood': 6.0,
              'major_flood': 12.0
          }
      
      def detect_flood_events(self, sensor_readings):
          """Scan for sensors exceeding thresholds"""
          events = []
          
          for reading in sensor_readings:
              if reading['flood_depth_inches'] >= self.thresholds['moderate_flood']:
                  event = self.create_flood_event(reading)
                  events.append(event)
          
          return events
      
      def create_flood_event(self, sensor_reading):
          """Create flood event record"""
          sensor = self.get_sensor_details(sensor_reading['sensor_id'])
          fvi_zone = self.get_fvi_for_location(sensor['latitude'], sensor['longitude'])
          
          return {
              'event_id': f"flood_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
              'sensor_id': sensor['sensor_id'],
              'location': sensor['neighborhood'],
              'borough': sensor['borough'],
              'severity': self.calculate_severity(sensor_reading['flood_depth_inches']),
              'flood_depth_inches': sensor_reading['flood_depth_inches'],
              'vulnerability_level': fvi_zone['vulnerability_category'],
              'estimated_affected_residents': fvi_zone['population'],
              'timestamp': sensor_reading['timestamp'],
              'status': 'active'
          }
  ```
- [ ] Create database schema:
  ```sql
  CREATE TABLE flood_events (
      event_id TEXT PRIMARY KEY,
      sensor_id TEXT,
      location TEXT,
      borough TEXT,
      severity TEXT,  -- MINOR, MODERATE, MAJOR
      flood_depth_inches REAL,
      vulnerability_level TEXT,
      estimated_affected_residents INTEGER,
      start_time TEXT,
      end_time TEXT,
      status TEXT,  -- active, resolved
      FOREIGN KEY (sensor_id) REFERENCES flood_sensors(sensor_id)
  );
  ```
- [ ] Implement alert notification system:
  - Dashboard notification (WebSocket)
  - Email notification (optional for demo)
  - Partner API webhook (next task)
- [ ] Create alert history view
- [ ] Test with simulated flood event

**Deliverable:** Automated flood event detection and alerting

---

### Day 19-20: Partner API Development (Nov 28-29)

**Goal:** API for partner calling system integration

**Tasks:**
- [ ] Create `api/partner_api.py`:
  ```python
  from flask import Blueprint, request, jsonify
  
  partner_api = Blueprint('partner_api', __name__)
  
  @partner_api.route('/api/trigger-wellness-checks', methods=['POST'])
  def trigger_wellness_checks():
      """
      Endpoint for FloodVoice to trigger wellness check campaign
      Partner calling system will call this to get resident list
      """
      data = request.json
      flood_event_id = data.get('flood_event_id')
      
      # Get flood event details
      event = get_flood_event(flood_event_id)
      
      # Get vulnerable residents in affected area
      residents = get_vulnerable_residents(
          zipcodes=event['affected_zipcodes'],
          vulnerability_level='HIGH'
      )
      
      # Create wellness check campaign
      campaign = create_wellness_campaign(event, residents)
      
      return jsonify({
          'campaign_id': campaign['id'],
          'residents_to_contact': len(residents),
          'resident_list': residents,  # [{name, phone, language, special_needs}]
          'status': 'initiated'
      })
  
  @partner_api.route('/api/wellness-check-result', methods=['POST'])
  def receive_wellness_check_result():
      """
      Webhook for partner system to report call results
      """
      data = request.json
      
      update_campaign_status(
          campaign_id=data['campaign_id'],
          resident_id=data['resident_id'],
          call_status=data['status'],  # completed, no_answer, needs_help
          notes=data.get('notes')
      )
      
      return jsonify({'success': True})
  ```
- [ ] Create mock vulnerable residents dataset:
  ```sql
  CREATE TABLE vulnerable_residents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      phone TEXT,
      zipcode TEXT,
      preferred_language TEXT,
      special_needs TEXT,  -- mobility, medical, elderly
      last_contact_date TEXT
  );
  ```
- [ ] Generate 500-1000 mock residents across high-FVI ZIP codes
- [ ] Create wellness campaign tracking:
  ```sql
  CREATE TABLE wellness_campaigns (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      campaign_id TEXT UNIQUE,
      flood_event_id TEXT,
      created_at TEXT,
      total_residents INTEGER,
      calls_completed INTEGER,
      calls_pending INTEGER,
      residents_needing_help INTEGER,
      status TEXT,  -- in_progress, completed
      FOREIGN KEY (flood_event_id) REFERENCES flood_events(event_id)
  );
  ```
- [ ] Create API documentation (Swagger/OpenAPI)
- [ ] Test API with Postman or curl
- [ ] Share API docs with partner developer

**Deliverable:** Partner API ready for integration

---

### Day 21: Historical Analysis View (Nov 30)

**Goal:** View past flood events and correlations

**Tasks:**
- [ ] Create `templates/historical.html`:
  - Date range picker
  - List of past flood events
  - Correlation accuracy metrics
  - Export to CSV button
- [ ] Create Flask route:
  ```python
  @app.route('/historical')
  def historical_analysis():
      events = get_flood_events(days_back=30)
      correlations = get_correlations(days_back=30)
      
      stats = {
          'total_events': len(events),
          'avg_correlation_accuracy': calculate_avg_accuracy(correlations),
          'most_affected_borough': get_most_affected_borough(events)
      }
      
      return render_template('historical.html', events=events, stats=stats)
  ```
- [ ] Add charts showing:
  - Flood events over time (line chart)
  - Correlation accuracy by borough (bar chart)
  - Sensor reliability (uptime %)
- [ ] Implement CSV export functionality
- [ ] Test with demo data

**Deliverable:** Historical analysis dashboard

**Week 3 Milestone:** ✅ Intelligence layer complete - AI insights + alerts + partner API

---

## 💎 WEEK 4: Polish, Testing & Demo Prep (Dec 1-8)

### Day 22-23: UI/UX Refinement (Dec 1-2)

**Goal:** Professional, polished interface

**Tasks:**
- [ ] Refine dashboard layout:
  - Consistent color scheme (blues/greens for water theme)
  - Responsive design (mobile-friendly)
  - Smooth animations and transitions
- [ ] Improve map visualization:
  - Custom sensor icons (water droplet shapes)
  - Animated pulse for active flooding
  - Better popup design with more details
- [ ] Add loading states and spinners
- [ ] Improve error messages and user feedback
- [ ] Add tooltips and help text
- [ ] Create logo and branding for FloodVoice
- [ ] Add "About" page explaining the project
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)

**Deliverable:** Polished, professional UI

---

### Day 24-25: Demo Data Preparation (Dec 3-4)

**Goal:** Compelling demo scenario

**Tasks:**
- [ ] Create realistic demo scenario:
  - **Location:** Astoria, Queens (high FVI area)
  - **Trigger:** Heavy rainfall event
  - **Timeline:** 6-hour flood event
- [ ] Prepare demo dataset:
  - 5-10 sensors showing progressive flooding (0" → 10" over 2 hours)
  - 20-30 community reports correlating with sensor spikes
  - Mix of urgency levels and sentiments
  - Strong correlations (80%+ match rate)
- [ ] Create demo script:
  1. Show baseline (normal conditions)
  2. Trigger flood event (sensor readings spike)
  3. Community reports appear on map
  4. AI generates insights
  5. Alert triggers wellness check campaign
  6. Show partner API call/response
  7. Display campaign status
- [ ] Pre-load demo data into database
- [ ] Create "Demo Mode" toggle to use pre-loaded data
- [ ] Test demo flow multiple times

**Deliverable:** Compelling demo scenario ready to present

---

### Day 26-27: Testing & Bug Fixes (Dec 5-6)

**Goal:** Stable, bug-free application

**Tasks:**
- [ ] Create test suite:
  ```python
  # tests/test_correlation.py
  def test_correlation_accuracy():
      reports = load_test_reports()
      sensors = load_test_sensors()
      correlations = correlation_engine.correlate(reports, sensors)
      assert len(correlations) > 0
      assert correlations[0]['correlation_strength'] in ['STRONG', 'MODERATE', 'WEAK']
  
  # tests/test_nlp.py
  def test_location_extraction():
      text = "Flooding on Atlantic Ave in Brooklyn"
      locations = nlp_engine.extract_location(text)
      assert 'Brooklyn' in locations
  
  # tests/test_api.py
  def test_partner_api():
      response = client.post('/api/trigger-wellness-checks', json={
          'flood_event_id': 'test_event_001'
      })
      assert response.status_code == 200
      assert 'campaign_id' in response.json
  ```
- [ ] Run all tests and fix failures
- [ ] Manual testing checklist:
  - [ ] Map loads correctly
  - [ ] Sensors display with correct colors
  - [ ] Real-time updates work
  - [ ] Correlations appear in feed
  - [ ] AI insights generate successfully
  - [ ] Alerts trigger correctly
  - [ ] Partner API responds properly
  - [ ] Historical view loads
  - [ ] Export to CSV works
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness testing
- [ ] Performance testing (page load <3 seconds)
- [ ] Fix all critical bugs

**Deliverable:** Stable, tested application

---

### Day 28-29: Documentation & Demo Prep (Dec 7-8)

**Goal:** Ready to present

**Tasks:**
- [ ] Update README.md with FloodVoice-specific content:
  - Project overview
  - Installation instructions
  - Demo instructions
  - API documentation
  - Screenshots
- [ ] Create demo presentation slides:
  - Problem statement
  - Solution overview
  - Live demo walkthrough
  - Technical architecture
  - Impact metrics
  - Next steps / funding ask
- [ ] Record backup demo video (in case of technical issues)
- [ ] Prepare talking points:
  - "Narrative to Numbers" concept
  - Community-centered approach
  - Vulnerable population focus
  - Real-time response capability
  - Scalability and expansion potential
- [ ] Practice demo 3-5 times
- [ ] Prepare for Q&A:
  - FloodNet API access
  - Data privacy concerns
  - Scalability questions
  - Cost estimates
  - Timeline for full deployment
- [ ] Final code review and cleanup
- [ ] Push final version to GitHub
- [ ] Deploy to demo environment (Heroku/Render/local)

**Deliverable:** Polished demo ready to present

---

## 🎯 DEMO DAY: December 9, 2025

### Pre-Demo Checklist (Morning of Dec 9)
- [ ] Test demo environment (internet connection, screen sharing)
- [ ] Load demo data
- [ ] Test all features one final time
- [ ] Have backup video ready
- [ ] Charge laptop, have charger ready
- [ ] Print presentation slides (backup)
- [ ] Arrive 15 minutes early

### Demo Flow (15-20 minutes)
1. **Introduction (2 min)**
   - Problem: Vulnerable populations during floods
   - Solution: FloodVoice platform

2. **Live Demo (10 min)**
   - Show baseline dashboard
   - Trigger flood event
   - Show correlations appearing
   - AI insights generation
   - Alert and wellness check trigger
   - Partner API integration

3. **Technical Overview (3 min)**
   - Architecture diagram
   - Data sources
   - NLP pipeline
   - Scalability

4. **Impact & Next Steps (3 min)**
   - Success metrics
   - Expansion plans
   - Funding ask
   - Partnership opportunities

5. **Q&A (5 min)**

### Success Criteria
- ✅ Demo runs smoothly without technical issues
- ✅ Audience understands "Narrative to Numbers" concept
- ✅ Positive feedback from NYC PRI Data Team
- ✅ Interest in funding/partnership
- ✅ Follow-up meeting scheduled

---

## 📊 Progress Tracking

### Weekly Check-ins
- **End of Week 1:** Foundation complete?
- **End of Week 2:** Core features working?
- **End of Week 3:** Intelligence layer ready?
- **End of Week 4:** Demo-ready?

### Risk Mitigation
- **FloodNet API unavailable:** Use mock data generator
- **NLP accuracy low:** Manual curation of demo data
- **Partner integration delayed:** Show API docs and mock response
- **Technical issues on demo day:** Use backup video

---

## 🚀 Post-Demo Action Items

### Immediate (Dec 10-15)
- [ ] Send thank-you email to NYC PRI team
- [ ] Incorporate feedback from demo
- [ ] Schedule follow-up meetings
- [ ] Update GitHub with final version

### Short-term (Dec 16-31)
- [ ] Secure funding commitment
- [ ] Onboard pilot community organizations
- [ ] Establish FloodNet partnership
- [ ] Complete partner calling system integration

### Long-term (2026 Q1)
- [ ] Production deployment
- [ ] Expand to all NYC flood-prone areas
- [ ] Multi-language support
- [ ] Mobile app development

---

**Build Plan Status:** Ready to Execute  
**Next Action:** Begin Day 1 tasks (Repository setup)  
**Questions/Blockers:** TBD

---

*This build plan is a living document. Update progress daily and adjust timeline as needed.*

