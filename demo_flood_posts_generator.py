#!/usr/bin/env python3
"""
Demo Flood Posts Generator for N2N Hackathon
Creates 20 compelling, realistic flood-related social media posts for demo
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
from textblob import TextBlob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_demo_flood_posts():
    """Create 20 compelling flood posts for hackathon demo"""
    
    # REALISTIC flood posts with high engagement potential
    demo_posts = [
        {
            'text': '🌊 EMERGENCY: Major flooding on Atlantic Ave in Brooklyn! Water up to car doors, people abandoning vehicles! This is climate change in action! #FloodEmergency #Brooklyn #ClimateChange',
            'borough': 'brooklyn',
            'location': 'Atlantic Avenue',
            'urgency_multiplier': 1.0,
            'engagement_boost': 500
        },
        {
            'text': '🚨 SUBWAY FLOODED: 4/5/6 trains at Union Square completely underwater! Thousands stranded, no service! MTA needs flood infrastructure NOW! #MTAFlooding #NYC #Emergency',
            'borough': 'manhattan',
            'location': 'Union Square',
            'urgency_multiplier': 0.9,
            'engagement_boost': 800
        },
        {
            'text': 'My Astoria basement flooded AGAIN 😭 Third time this year! Landlord says "not my problem" but where else can we go? #FloodVictim #Queens #Housing',
            'borough': 'queens',
            'location': 'Astoria',
            'urgency_multiplier': 0.7,
            'engagement_boost': 200
        },
        {
            'text': '🆘 HELP NEEDED: Elderly neighbors trapped by flooding on Grand Concourse! Water rising fast, first responders overwhelmed! #FloodRescue #Bronx #Community',
            'borough': 'bronx',
            'location': 'Grand Concourse',
            'urgency_multiplier': 1.0,
            'engagement_boost': 600
        },
        {
            'text': 'Staten Island Ferry terminal flooded! No service to Manhattan. How are essential workers supposed to get to work?? #SIFerry #Flooding #Transportation',
            'borough': 'staten_island',
            'location': 'Ferry Terminal',
            'urgency_multiplier': 0.8,
            'engagement_boost': 300
        },
        {
            'text': 'FDR Drive completely underwater near Brooklyn Bridge! Cars floating like toys! This infrastructure was NOT built for climate change! #FDRFlooding #Infrastructure',
            'borough': 'manhattan',
            'location': 'FDR Drive',
            'urgency_multiplier': 0.9,
            'engagement_boost': 700
        },
        {
            'text': 'Coney Island boardwalk getting DESTROYED by storm surge! Businesses underwater, people evacuating! #ConeyIsland #StormSurge #Brooklyn',
            'borough': 'brooklyn',
            'location': 'Coney Island',
            'urgency_multiplier': 0.8,
            'engagement_boost': 400
        },
        {
            'text': 'Queens Blvd flooded from Elmhurst to Forest Hills! Buses can\'t run, people walking through knee-deep water! #QueensBlvd #Flooding #PublicTransit',
            'borough': 'queens',
            'location': 'Queens Boulevard',
            'urgency_multiplier': 0.7,
            'engagement_boost': 250
        },
        {
            'text': '🌊 LIVE UPDATE: Hunts Point flooding forcing families from homes! Red Cross setting up shelter at local school! #HuntsPoint #Bronx #RedCross',
            'borough': 'bronx',
            'location': 'Hunts Point',
            'urgency_multiplier': 0.8,
            'engagement_boost': 350
        },
        {
            'text': 'Belt Parkway CLOSED due to flooding! Traffic nightmare across Brooklyn! When will NYC invest in proper drainage?? #BeltParkway #TrafficAlert #Brooklyn',
            'borough': 'brooklyn',
            'location': 'Belt Parkway',
            'urgency_multiplier': 0.6,
            'engagement_boost': 180
        },
        {
            'text': 'My Lower East Side apartment building has 3 feet of water in basement! All our storage, laundry, everything destroyed! #LES #FloodDamage #Manhattan',
            'borough': 'manhattan',
            'location': 'Lower East Side',
            'urgency_multiplier': 0.6,
            'engagement_boost': 150
        },
        {
            'text': '🚨 FLASH FLOOD WARNING: Flushing Meadows completely underwater! Cars abandoned everywhere! This is unprecedented! #FlushingMeadows #Queens #FlashFlood',
            'borough': 'queens',
            'location': 'Flushing Meadows',
            'urgency_multiplier': 0.9,
            'engagement_boost': 450
        },
        {
            'text': 'South Bronx drainage system FAILED! Streets are rivers, manhole covers popping off! Environmental racism in action! #SouthBronx #EnvironmentalJustice',
            'borough': 'bronx',
            'location': 'South Bronx',
            'urgency_multiplier': 0.8,
            'engagement_boost': 320
        },
        {
            'text': 'St. George Terminal flooded! Staten Island completely cut off from rest of NYC! This is what climate vulnerability looks like! #StGeorge #ClimateVulnerability',
            'borough': 'staten_island',
            'location': 'St. George',
            'urgency_multiplier': 0.7,
            'engagement_boost': 280
        },
        {
            'text': 'Williamsburg waterfront flooding! Luxury condos getting flooded while public housing gets ignored! #Williamsburg #Brooklyn #Inequality',
            'borough': 'brooklyn',
            'location': 'Williamsburg',
            'urgency_multiplier': 0.6,
            'engagement_boost': 220
        },
        {
            'text': '🌊 Central Park flooded! Never seen anything like this! Sheep Meadow is now Sheep Lake! Climate change is HERE! #CentralPark #Manhattan #ClimateChange',
            'borough': 'manhattan',
            'location': 'Central Park',
            'urgency_multiplier': 0.7,
            'engagement_boost': 500
        },
        {
            'text': 'Jackson Heights subway station flooded! 7 train not running! How are essential workers getting to Manhattan?? #JacksonHeights #Queens #7Train',
            'borough': 'queens',
            'location': 'Jackson Heights',
            'urgency_multiplier': 0.7,
            'engagement_boost': 200
        },
        {
            'text': 'Fordham Road underwater! Businesses closing, people stranded! Bronx always gets hit hardest! #FordhamRoad #Bronx #FloodJustice',
            'borough': 'bronx',
            'location': 'Fordham Road',
            'urgency_multiplier': 0.6,
            'engagement_boost': 180
        },
        {
            'text': 'Great Kills flooding forcing evacuations! Staten Island forgotten again! We need federal flood protection NOW! #GreatKills #StatenIsland #FEMA',
            'borough': 'staten_island',
            'location': 'Great Kills',
            'urgency_multiplier': 0.8,
            'engagement_boost': 250
        },
        {
            'text': '🆘 URGENT: Red Hook completely flooded! NYCHA residents trapped in buildings! This is a humanitarian crisis! #RedHook #Brooklyn #NYCHA #Crisis',
            'borough': 'brooklyn',
            'location': 'Red Hook',
            'urgency_multiplier': 1.0,
            'engagement_boost': 600
        }
    ]
    
    # Process posts into database format
    processed_posts = []
    base_time = datetime.now() - timedelta(hours=2)  # Posts from last 2 hours
    
    for i, post in enumerate(demo_posts):
        # Calculate realistic engagement
        base_likes = random.randint(50, 200) + post['engagement_boost']
        shares = int(base_likes * random.uniform(0.1, 0.3))
        comments = int(base_likes * random.uniform(0.05, 0.15))
        engagement_score = base_likes + (shares * 3) + (comments * 2)
        
        # Calculate sentiment
        sentiment = TextBlob(post['text']).sentiment
        
        # Calculate urgency score
        base_urgency = (abs(sentiment.polarity) * 0.4 + 
                       sentiment.subjectivity * 0.3 + 
                       (engagement_score / 1000) * 0.3)
        urgency_score = min(base_urgency * post['urgency_multiplier'], 1.0)
        
        # Determine urgency level
        if urgency_score > 0.7:
            urgency_level = 'HIGH'
        elif urgency_score > 0.4:
            urgency_level = 'MODERATE'
        else:
            urgency_level = 'LOW'
        
        # Post timestamp (spread over last 2 hours)
        post_time = base_time + timedelta(minutes=random.randint(0, 120))
        
        processed_posts.append({
            'post_id': f"demo_flood_{i+1:02d}",
            'text': post['text'],
            'category': 'flood_concern',
            'borough': post['borough'],
            'location': post['location'],
            'post_date': post_time.isoformat(),
            'likes': base_likes,
            'shares': shares,
            'comments': comments,
            'engagement_score': engagement_score,
            'sentiment_polarity': round(sentiment.polarity, 3),
            'sentiment_subjectivity': round(sentiment.subjectivity, 3),
            'sentiment_label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral',
            'urgency_score': round(urgency_score, 3),
            'urgency_level': urgency_level,
            'flood_mentions': True,
            'health_mentions': False,
            'environmental_mentions': 'climate' in post['text'].lower() or 'environment' in post['text'].lower(),
            'data_source': 'DEMO_SOCIAL_MEDIA',
            'ingestion_date': datetime.now().isoformat(),
            'processing_version': 'DEMO_1.0'
        })
    
    return processed_posts

def save_demo_posts_to_database(posts):
    """Save demo posts to database, replacing existing social media data"""
    try:
        conn = sqlite3.connect('public_health_data.db')
        
        # Clear existing social media posts
        conn.execute('DELETE FROM social_media_posts')
        
        # Insert demo posts
        df = pd.DataFrame(posts)
        df.to_sql('social_media_posts', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved {len(posts)} demo flood posts to database")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving demo posts: {e}")
        return False

def main():
    """Generate and save demo flood posts"""
    logger.info("🎬 Creating demo flood posts for hackathon...")
    
    # Generate posts
    posts = create_demo_flood_posts()
    
    # Save to database
    success = save_demo_posts_to_database(posts)
    
    if success:
        logger.info("🎯 Demo flood posts ready for hackathon!")
        logger.info("📊 Summary:")
        
        # Print summary
        df = pd.DataFrame(posts)
        logger.info(f"   Total posts: {len(posts)}")
        logger.info(f"   Borough distribution: {df['borough'].value_counts().to_dict()}")
        logger.info(f"   Urgency levels: {df['urgency_level'].value_counts().to_dict()}")
        logger.info(f"   Total engagement: {df['engagement_score'].sum():,}")
        logger.info(f"   Average urgency: {df['urgency_score'].mean():.3f}")
        
        return posts
    else:
        logger.error("❌ Failed to create demo posts")
        return None

if __name__ == "__main__":
    demo_posts = main()
