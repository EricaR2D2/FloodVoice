-- FloodVoice Demo Seed Data
-- Run this AFTER running schema.sql in the Supabase SQL Editor
-- Covers: Red Hook (Brooklyn), Canarsie (Brooklyn), Hunts Point (Bronx), South Bronx (Bronx)
-- All phone numbers are fictional placeholders.

-- Placeholder liaison_id (no real auth user needed for demo)
-- Replace '00000000-0000-0000-0000-000000000000' with a real user UUID after auth is configured.

INSERT INTO public.residents (id, liaison_id, name, phone_number, age, address, health_conditions, zip_code, language, status)
VALUES
  -- RED HOOK, BROOKLYN (11231) — high flood risk, mixed community
  ('aaaaaaaa-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000000','Maria Santos','+17185550101',72,'142 Van Dyke St, Apt 2A','Diabetes, hypertension','11231','es','pending'),
  ('aaaaaaaa-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000000','James Williams','+17185550102',68,'89 King St, Apt 1B','Type 2 diabetes','11231','en','safe'),
  ('aaaaaaaa-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000000','Carmen Rivera','+17185550103',79,'215 Commerce St, Apt 3C','Mobility limitations, arthritis','11231','es','distress'),
  ('aaaaaaaa-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000000','Anthony Johnson','+17185550104',45,'31 Coffey St, Apt B','PTSD, asthma','11231','en','pending'),
  ('aaaaaaaa-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000000','Hyun-Sook Park','+17185550105',81,'7 Richards St, Apt 4D','Heart disease, limited mobility','11231','ko','pending'),
  ('aaaaaaaa-0000-0000-0000-000000000006','00000000-0000-0000-0000-000000000000','Darnell Thompson','+17185550106',55,'63 Van Brunt St, Apt 1A','Asthma, COPD','11231','en','safe'),

  -- CANARSIE, BROOKLYN (11236) — Caribbean community, low-lying streets
  ('bbbbbbbb-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000000','Claudette Brown','+17185550201',74,'1420 Flatlands Ave, Apt 5B','Heart disease, high blood pressure','11236','en','pending'),
  ('bbbbbbbb-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000000','Winston Clarke','+17185550202',67,'832 E 86th St, Apt 2A','Diabetes, kidney disease','11236','en','safe'),
  ('bbbbbbbb-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000000','Paulette Francis','+17185550203',83,'19 Rockaway Pkwy, Apt 6C','Mobility limitations, dementia','11236','en','pending'),
  ('bbbbbbbb-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000000','Mikaela Joseph','+17185550204',39,'204 Remsen Ave, Apt 3A','Epilepsy','11236','en','pending'),
  ('bbbbbbbb-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000000','Trevor Campbell','+17185550205',58,'566 E 93rd St, Apt 1B','COPD, asthma','11236','en','pending'),
  ('bbbbbbbb-0000-0000-0000-000000000006','00000000-0000-0000-0000-000000000000','Yvette Daley','+17185550206',71,'1102 Ralph Ave, Apt 4D','Arthritis, hypertension','11236','en','pending'),

  -- HUNTS POINT, BRONX (10474) — heavily Latino, industrial waterfront
  ('cccccccc-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000000','Rosa Gutierrez','+17185550301',66,'860 Hunts Point Ave, Apt 2B','Diabetes, obesity','10474','es','pending'),
  ('cccccccc-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000000','Miguel Torres','+17185550302',78,'45 Spofford Ave, Apt 1A','Heart disease, stroke history','10474','es','distress'),
  ('cccccccc-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000000','Luz Perez','+17185550303',54,'112 Barry St, Apt 3C','Severe asthma','10474','es','pending'),
  ('cccccccc-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000000','Carlos Mendoza','+17185550304',85,'33 Lafayette Ave, Apt 2A','Mobility limitations, oxygen dependent','10474','es','pending'),
  ('cccccccc-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000000','Ana Flores','+17185550305',47,'678 Manida St, Apt 5D','Anxiety, asthma','10474','es','safe'),
  ('cccccccc-0000-0000-0000-000000000006','00000000-0000-0000-0000-000000000000','Jose Ortega','+17185550306',72,'99 Tiffany St, Apt 1B','Heart disease, diabetes','10474','es','pending'),

  -- SOUTH BRONX (10454) — mixed Latino/Black community, Bruckner/Willis corridor
  ('dddddddd-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000000','Denise Jackson','+17185550401',61,'312 Willis Ave, Apt 3A','Kidney disease, diabetes','10454','en','pending'),
  ('dddddddd-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000000','Roberto Diaz','+17185550402',76,'45 Bruckner Blvd, Apt 2C','Stroke history, hypertension','10454','es','distress'),
  ('dddddddd-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000000','Sharonda Robinson','+17185550403',48,'890 E 138th St, Apt 1B','Diabetes, obesity','10454','en','pending'),
  ('dddddddd-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000000','Emmanuel Williams','+17185550404',33,'156 Third Ave, Apt 4A',null,'10454','en','safe'),
  ('dddddddd-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000000','Marisol Vega','+17185550405',69,'721 Exterior St, Apt 2B','COPD, hypertension','10454','es','pending'),
  ('dddddddd-0000-0000-0000-000000000006','00000000-0000-0000-0000-000000000000','Franklin Hayes','+17185550406',77,'38 E 149th St, Apt 3C','Mobility limitations, heart disease','10454','en','pending');

-- Demo call logs — sentiment_score 1-10 (higher = more urgent/distress)
-- 1-3 = stable, 4-5 = moderate, 6-7 = elevated, 8-10 = critical
INSERT INTO public.call_logs (id, resident_id, vapi_call_id, summary, risk_label, tags, sentiment_score, key_topics, created_at)
VALUES
  ('11111111-0000-0000-0000-000000000001','aaaaaaaa-0000-0000-0000-000000000003','demo-call-001','Resident reports 6 inches of water in basement apartment. Unable to move furniture independently. Has not taken morning medication.','distress','{flooding,medication,evacuation}',9,'flooding, mobility, medication',now() - interval '2 hours'),
  ('11111111-0000-0000-0000-000000000002','cccccccc-0000-0000-0000-000000000002','demo-call-002','Resident is alone. Water reached front door. Oxygen tank supply running low. Family in Puerto Rico, no local contacts.','distress','{flooding,medical,isolation}',9,'oxygen, flooding, isolation',now() - interval '90 minutes'),
  ('11111111-0000-0000-0000-000000000003','dddddddd-0000-0000-0000-000000000002','demo-call-003','Water outside but not inside yet. Resident is very anxious. Had a stroke 8 months ago and cannot walk well. Concerned about power going out.','distress','{power,flooding,medical}',8,'stroke, power outage, anxiety',now() - interval '3 hours'),
  ('11111111-0000-0000-0000-000000000004','bbbbbbbb-0000-0000-0000-000000000003','demo-call-004','Resident is 83 years old and confused about what to do. Her caregiver has not arrived. No food in the house for the day.','distress','{food,isolation,medical}',7,'dementia, caregiver, food',now() - interval '1 hour'),
  ('11111111-0000-0000-0000-000000000005','cccccccc-0000-0000-0000-000000000004','demo-call-005','Water below the door threshold but rising slowly. Resident cannot leave without assistance. Oxygen concentrator is plugged in — fears power loss.','distress','{flooding,medical,power}',8,'oxygen, flooding, power',now() - interval '45 minutes'),
  ('11111111-0000-0000-0000-000000000006','aaaaaaaa-0000-0000-0000-000000000001','demo-call-006','Resident reports street is flooded but her floor is dry. She has insulin in the refrigerator and is worried about power outage affecting medication storage.','elevated','{flooding,medication,power}',6,'insulin, power, flooding',now() - interval '4 hours'),
  ('11111111-0000-0000-0000-000000000007','dddddddd-0000-0000-0000-000000000001','demo-call-007','Water came under the door about an inch. Neighbor helped move items off floor. Resident is calm but running low on dialysis supplies.','elevated','{flooding,medical}',6,'dialysis, flooding',now() - interval '5 hours'),
  ('11111111-0000-0000-0000-000000000008','bbbbbbbb-0000-0000-0000-000000000001','demo-call-008','Street flooding reported. Resident is on the second floor and feels safe. Blood pressure medication was refilled yesterday. Checking in as requested.','stable','{flooding}',3,'safe, second floor, medication',now() - interval '6 hours'),
  ('11111111-0000-0000-0000-000000000009','aaaaaaaa-0000-0000-0000-000000000002','demo-call-009','Resident confirmed safe. Lives on third floor. Has enough food and medication for three days. Son checked in earlier.','stable','{shelter}',2,'safe, third floor, supplies',now() - interval '7 hours'),
  ('11111111-0000-0000-0000-000000000010','cccccccc-0000-0000-0000-000000000001','demo-call-010','Basement apartment with minor seepage. Resident moved to upstairs neighbor. Has one day of insulin supply. Needs pharmacy contact.','moderate','{flooding,medication,shelter}',5,'insulin, flooding, relocated',now() - interval '8 hours');

