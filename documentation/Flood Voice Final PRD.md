# **Flood Voice PRD**

**Project:** Flood Voice  
**Owner:** Jessenia, Ethan, Erica, Josue, Kelvin, Shanell  
**Date:** November 23rd, 2025

## **Problem**

Vulnerable NYC residents—specifically the elderly, disabled, and those living in basement apartments—are disproportionately impacted by flash floods yet lack resilient channels to signal for help. Current emergency alert systems (WEA/Notify NYC) rely on text-based, smartphone-centric notifications that this demographic often misses or cannot understand. Furthermore, during surge events like Hurricane Ida, 911 and 311 systems are overwhelmed by 10,000+ calls per hour, making it impossible for first responders to differentiate between a flooded basement entrapment (life-threatening) and street flooding (non-urgent). This "blindness" leads to preventable delays in rescue operations and loss of life.

**Supporting Context:**

* **Basement Risk:** NYC has \~50,000 to 100,000 basement apartments, housing a population that is often undocumented or non-English speaking.  
* **Ida’s Toll:** Hurricane Ida (2021) killed 11 NYC residents, the majority of whom were trapped in basement apartments and unable to self-evacuate or contact help in time.  
* **The Digital Divide:** Approximately 15% of NYC’s population is elderly (65+), with high rates of digital exclusion, making app-based warnings ineffective.  
* **Infrastructure Failure:** Reliance on cellular data networks is fragile; voice voice/landline connectivity remains the most accessible layer of communication for this demographic.

## **Opportunity**

Flood Voice is a high-leverage "Community Triage" platform. It enables Community Based Organizations (CBOs) and family liaisons to proactively monitor thousands of at-risk residents simultaneously during a flood event. By using AI to automate voice-based welfare checks, we can **convert thousands of isolated, qualitative cries for help into a structured, prioritized dataset.** This reduces the noise for emergency responders and ensures that human attention is focused immediately on those who are trapped or in danger.

**Market Opportunity:**

* **Target Population:** 1.2 million NYC residents live in FEMA NFHL zones. Capturing even 5% of the most vulnerable via CBO partnerships represents 60,000 lives protected.  
* **City & State Contracts:** NYC Emergency Management and the Department of Health actively seek solutions to address the "communication gap" identified in the post-Ida Action Plan.  
* **Scalability:** The "Liaison Model" is replicable for other hazards (Heat Waves, Blizzards) and other coastal cities (Miami, Boston, New Orleans).

## **Users & Needs**

### **WHO: User Types**

* **Primary User (The Registrant):** **The Community Liaison ("Ethan").** A family member, building superintendent, or caseworker at a local non-profit. They are tech-savvy and responsible for the safety of a "pod" of vulnerable people.  
* **End User (The Recipient):** **The Vulnerable Resident ("Maria").** An elderly, disabled, or non-English speaking resident living in a high-risk zone. They may not own a smartphone and require low-friction interaction.  
* **Secondary User:** **CBO Coordinator.** A director at a community center needing a high-level view of member safety across a neighborhood.

### **NEEDS: User Story Format**

**1\. Primary User: Community Liaison ("Ethan")**

* "As a community liaison, I need to register my non-tech-savvy grandmother for alerts, so she is protected without needing to download an app she doesn't understand."  
* "As a liaison, I need to know immediately if my 'pod' members are safe or in danger during a storm, so I don't have to panic-dial 20 people who might not answer."  
* "As a liaison, I need clear instructions on who to escalate to 911, so I don't waste emergency resources on false alarms."

**2\. End User: Vulnerable Resident ("Maria")**

* "As a Spanish-speaking senior, I need to hear emergency instructions in my own language, so I fully understand the risk."  
* "As a resident with limited mobility, I need a hands-free or simple way to say 'I need help,' so I can signal distress even if I cannot physically type a text message."

**3\. Secondary User: CBO Coordinator**

* "As a CBO Director, I need to upload a list of our 500 senior members, so we can mass-monitor their safety during a heatwave or flood without manual phone trees."

## **Proposed Solution**

Proposed Solution An automated, voice-first triage system with a "Human-in-the-Loop" trigger. Flood Voice empowers Community Liaisons to create a "pod" of vulnerable residents. When a flood risk is detected via **real-time FloodNet sensors** (primary trigger) or **NWS alerts** (secondary fail-safe), it notifies the Liaison, who must confirm the local danger and activate the emergency check.

Before a Flood risk is detected door to door recruitment of liaisons and vulnerable residents occurs using NYC flood data on known at risk basement apartments and flood zones. At risk individuals could also receive preemptive flood warnings that ask if they have recently experienced health/risk changes? But might be a hippa problem?

Once activated, the system triggers simultaneous outbound calls to all subscribed residents. The resident simply answers the phone and speaks naturally ("I'm okay" or "Water is coming in"). Our AI analyzes these voice responses in real-time, transcribes them, and categorizes them by risk level on the Liaison's dashboard.

### **TOP 3 MVP VALUE PROPS:**

**1\. The Vitamin (Accessibility): Zero-Friction Protection.** The vulnerable resident requires absolutely no behavior change. They do not need a smartphone, an app, or a login. If they have a working phone number (landline or cell), they are protected. The barrier to entry is zero.

**2\. The Painkiller (Scale): Concurrent Triage.** Currently, a caseworker can check on \~10 people per hour manually. Flood Voice allows that same caseworker to check on 500 people in 60 seconds. This massively amplifies the capacity of community organizations during a crisis.

**3\. The Steroid (Intelligence): Narrative-to-Data.** We replace binary "Yes/No" inputs with rich sentiment analysis. By analyzing the *content* of the voice response (e.g., detecting keywords like "trapped," "basement," "electricity"), we provide a risk score (ex. Distress, Unresponsive, Safe, etc.) with context that a standard panic button cannot, giving responders critical situational awareness before they arrive. We also provide richer data for those analyzing floods in the future.

## **Goals & Non-Goals**

### **GOALS**

* **User Safety Outcome:** Successfully verify the safety status (Safe vs. Needs Help) of **85%** of contacted residents within **15 minutes** of the trigger event.  
* **System Accuracy:** Achieve **90% accuracy** in AI sentiment classification (correctly distinguishing between "I am safe" and "I need help") to prevent dispatcher fatigue.  
* **Escalation Reliability:** Ensure **100%** of "Distress" classified calls result in an immediate SMS notification to the designated Liaison.

### **NON-GOALS**

* **No Automatic 911 Dispatch:** We will **not** automatically route calls to 911 in the MVP. This avoids liability and regulatory hurdles. The decision to call 911 remains with the human Liaison.  
* **No Bi-Directional AI Conversation:** The MVP will not feature a conversational "chatbot" that asks follow-up questions. It is a "Prompt & Record" model to minimize latency and technical failure points.  
* **No GPS Tracking:** We rely on the static address provided during registration. We will not track real-time device location in the MVP to protect privacy and simplify the tech stack.

## **Success Metrics**

| Goal | Signal (Behavior) | Metric (Measurement) | Target (Success) |
| :---- | :---- | :---- | :---- |
| **Speed to Insight** | System processes voice audio and updates dashboard status. | **Time-to-Dashboard** (seconds from call end). | \< 10 seconds |
| **Adoption Friction** | Liaisons successfully register a vulnerable person (ex. grandmother.) | **Onboarding Completion Rate**. | \> 80% |
| **Triage Efficiency** | Liaison views the dashboard and identifies priority cases. | **Resolution Rate** (% of list marked "Safe" or "Escalated"). | \> 90% in 1 hr |
| **System Reliability** | Outbound calls connect to the resident's phone. | **Call Connection Rate**. | \> 95% |

## **Requirements**

**Organization: User Journey Priority Legend:**

* **\[P0\] MVP:** Must-have for the 3-week pilot demo.  
* **\[P1\] Important:** High value, but can be faked/manual for demo.  
* **\[P2\] Nice-to-Have:** Post-pilot roadmap.

**JOURNEY 1: Registration & Onboarding (Pre-Disaster)**

* **\[P2\] Flood Zone Campaign:** Campaign to sign up liaisons with targeted locations based on flood risk data.  
* **\[P0\] Liaison Dashboard:** A web interface where "Ethan" can create an account and manage his "pod" of vulnerable residents.  
* **\[P2\] Nearby Liaisons:** Ability to find another liaison who lives in or nearby grandma’s building.  
* **\[P0\] Vulnerability Profiling:** Ability to tag each resident with specific risk factors (e.g., "Basement Dweller," "Non-Ambulatory," "Vision Impaired").  
* **\[P0\] Liaison Attestation (MVP Consent):** Instead of an automated SMS loop, the Liaison must check a mandatory box during registration: *"I certify that I have obtained verbal consent from this resident to receive emergency calls."* (Automated verification deferred to V2).  
* **\[P1\] Language Selection:** Liaison can select the preferred language for the AI voice interface (English/Spanish/Mandarin).

**JOURNEY 2: The "Wellbeing Check" (Hybrid Trigger)** *Context: The "Human-in-the-Loop" workflow. The system detects the risk, but the Liaison makes the final call to avoid false alarms.*

* **\[P0\] Automated "Wake Up" Alert:** System monitors NWS feeds (or a mock trigger for MVP) and sends an SMS/WhatsApp to the Liaison: *"Flood Risk Detected in your zone. Click here to open dashboard."*  
* **\[P0\] The "Dead Man's Switch" (Manual Trigger):** The outbound calls to vulnerable residents **do not start** until the Liaison logs in and clicks the "Start Emergency Check-in" button.  
* **\[P0\] Concurrent Dialing:** Once the button is clicked, the backend initiates batch calls to all registered numbers in the pod.  
* **\[P0\] Voice Capture:** System records the resident's response for up to 30 seconds.  
* **\[P0\] Safety-First Scripting:** The voice agent must explicitly state: *"If this is a life-threatening medical emergency, hang up and dial 911 immediately"* before asking for status.

### **JOURNEY 3: Analysis & Escalation (Post-Call)**

* **\[P0\]** **Transcription & Keyword Spotting:** AI converts speech to text and scans for trigger words (e.g., "Help," "Water," "Stuck") to assign a risk score.  
* **\[P0\]** **Real-Time Dashboard Updates:** Liaison's view updates instantly via WebSocket without page refresh (Green/Red/Gray status indicators).  
* **\[P0\]** **The "Fail-Safe" SMS:** If a resident is marked "Unresponsive" or "Distress," the system automatically sends an SMS to the Liaison's phone urging immediate manual action.  
* **\[P1\]** **Audio Playback:** Liaison can click a button on the dashboard to listen to the specific audio recording of the distress call for verification.  
* **\[P0\]** **Escalation:** If the resident is marked in “Distress” or “Unresponsive”, the liaison may attempt an in person checkin, (**\[p2\]** request a check-in from a nearby liaison,) and call 911 if needed. **\[P1\]** With one click.  
* **\[P1\]** **Updates:** data from recent flood reports can be used by CBO or liaison to request repairs/ allocate resources better in the future.

## **Appendix**

* **Tech Stack:** React (Frontend), Node.js (Backend), Twilio Programmable Voice (Telephony), OpenAI Whisper (Transcription), Supabase (Database).  
* **Regulatory Reference (MVP Strategy):** For the pilot, we rely on **"Prior Express Consent"** obtained verbally by the Liaison. The Liaison assumes responsibility for this consent via the checkbox attestation in Journey 1\.  
* **Data Privacy:** All voice recordings are encrypted at rest and accessible only to the registered Liaison.  
* **CBO:** A Community-Based Organization (CBO) is typically a non-profit entity that operates within a specific community or geographical area.  
* **FloodNet NYC:** Our data dashboard was developed in partnership with FieldKit. The main page features a map view, allowing users to view all flood sensor readings in real time. Clicking on a sensor icon directs users to a data view page, where users can interact with historic time series data from a specific sensor.

# Integrated FloodVoice System Architecture

# Two-Layer System Design

   LAYER 1: MONITORING DASHBOARD                
  (FloodNet Sensors \+ Real-Time Detection)             
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            
│        Live Map  			  Sensor        			Flood       
│       (FloodNet)  		 	 Readings    			  Alerts        
│  └──────────────┘  └──────────────┘  └──────────────┘            
│   Monitors: 50+ sensors across NYC                                 
│  Detects: Flood depth \> threshold in vulnerable zones            
│  Triggers: Alert to CBO coordinators & liaisons                  
└───────────────────────────────────────────────────────────  
                              ↓  
                    FLOOD DETECTED IN ZONE  
                              ↓  
    LAYER 2: RESPONSE DASHBOARD                      
│              (Liaison Pod Management \+ Voice Calls)             
│                                                                  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            
│ 	  Liaison     	 		 Manual     	  	 Call Status  
│  	  Alert       			 Trigger     		 Dashboard               
│  └──────────────┘  └──────────────┘  └──────────────┘          
│  Notifies: Liaisons in affected ZIP codes                         
│  Activates: Liaison clicks "Start Emergency Check-in"          
│  Executes: Batch voice calls to vulnerable residents              
└───────────────────────────────────────────────────────────

