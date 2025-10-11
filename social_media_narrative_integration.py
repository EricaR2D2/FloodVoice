#!/usr/bin/env python3
"""
Social Media Narrative Integration for N2N Hackathon
Converting Community Voices to Quantified Insights

This script processes social media narratives about health, flooding, and environmental
concerns in NYC, converting them to quantified metrics for dashboard integration.
"""

import os
import requests
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np
import json
import re
from textblob import TextBlob
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialMediaNarrativeProcessor:
    def __init__(self, data_dir="social_media_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = "public_health_data.db"
        
        # NYC-specific keywords for health and environmental concerns
        self.health_keywords = [
            'asthma', 'breathing', 'respiratory', 'cough', 'allergies', 'sick', 'hospital', 'emergency room',
            'air quality', 'pollution', 'smog', 'health department', 'covid', 'flu', 'illness'
        ]
        
        self.flood_keywords = [
            'flood', 'flooding', 'water damage', 'storm surge', 'hurricane', 'rain', 'drainage',
            'basement flooded', 'street flooding', 'subway flooding', 'storm drain', 'evacuation'
        ]
        
        self.environmental_keywords = [
            'air quality', 'pollution', 'toxic', 'contamination', 'environmental', 'climate',
            'heat wave', 'extreme weather', 'infrastructure', 'public health', 'safety'
        ]
        
        # NYC borough hashtags and location indicators
        self.nyc_locations = {
            'manhattan': ['#manhattan', '#midtown', '#uppereastside', '#lowereastside', '#harlem', '#chinatown'],
            'brooklyn': ['#brooklyn', '#williamsburg', '#parkslope', '#bedstuy', '#crownheights', '#dumbo'],
            'queens': ['#queens', '#astoria', '#flushing', '#longislandcity', '#jackson heights', '#elmhurst'],
            'bronx': ['#bronx', '#southbronx', '#fordham', '#huntspoint', '#mott haven'],
            'staten_island': ['#statenisland', '#st george', '#new dorp', '#tottenville']
        }
    
    def create_mock_social_media_data(self, num_posts=1000):
        """Create realistic mock social media data for hackathon demo"""
        logger.info(f"Creating {num_posts} mock social media posts...")
        
        try:
            # Template posts for different categories
            health_templates = [
                "Air quality is terrible in {location} today. My {condition} is acting up again. #NYC #AirQuality",
                "Another trip to the ER because of {condition}. When will {location} address the air pollution? #PublicHealth",
                "Kids can't play outside in {location} - air quality index is through the roof! #HealthAlert",
                "Asthma attacks increasing in our neighborhood. Something needs to be done about {location} air quality.",
                "Hospital wait times are crazy in {location}. So many people with respiratory issues today."
            ]
            
            flood_templates = [
                "Street flooding again in {location}! This happens every time it rains. #Flooding #NYC",
                "Basement flooded AGAIN in {location}. City needs better drainage infrastructure! #FloodDamage",
                "Subway station at {location} completely flooded. How are we supposed to get to work? #MTAFlooding",
                "Storm surge warnings for {location}. Time to move everything upstairs again. #StormSurge",
                "Third time this month - {location} streets are underwater after heavy rain. #UrbanFlooding"
            ]
            
            environmental_templates = [
                "Air quality alert for {location} - staying indoors today. #AirPollution #EnvironmentalHealth",
                "Heat wave hitting {location} hard. Elderly neighbors struggling without AC. #ClimateChange",
                "Construction dust in {location} is making everyone sick. Where's the oversight? #Pollution",
                "Chemical smell in {location} - anyone else notice this? Worried about health impacts. #Environmental",
                "Green space in {location} being destroyed for development. We need more trees, not less! #Environment"
            ]
            
            # Generate realistic posts
            posts = []
            for i in range(num_posts):
                # Random date within last 6 months
                days_ago = random.randint(0, 180)
                post_date = datetime.now() - timedelta(days=days_ago)
                
                # Random location
                borough = random.choice(list(self.nyc_locations.keys()))
                location_tags = self.nyc_locations[borough]
                location = random.choice(location_tags).replace('#', '').title()
                
                # Random post type
                post_type = random.choice(['health', 'flood', 'environmental'])
                
                if post_type == 'health':
                    template = random.choice(health_templates)
                    condition = random.choice(['asthma', 'allergies', 'breathing problems', 'cough'])
                    text = template.format(location=location, condition=condition)
                    category = 'health_concern'
                elif post_type == 'flood':
                    template = random.choice(flood_templates)
                    text = template.format(location=location)
                    category = 'flood_concern'
                else:
                    template = random.choice(environmental_templates)
                    text = template.format(location=location)
                    category = 'environmental_concern'
                
                # Add engagement metrics
                likes = random.randint(0, 500)
                shares = random.randint(0, 100)
                comments = random.randint(0, 50)
                
                # Calculate sentiment
                sentiment = TextBlob(text).sentiment
                
                posts.append({
                    'post_id': f"post_{i:06d}",
                    'text': text,
                    'category': category,
                    'borough': borough,
                    'location': location,
                    'post_date': post_date.isoformat(),
                    'likes': likes,
                    'shares': shares,
                    'comments': comments,
                    'engagement_score': likes + (shares * 3) + (comments * 2),
                    'sentiment_polarity': round(sentiment.polarity, 3),
                    'sentiment_subjectivity': round(sentiment.subjectivity, 3),
                    'sentiment_label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral'
                })
            
            # Create DataFrame
            df = pd.DataFrame(posts)
            
            # Save to CSV
            csv_file = self.data_dir / "mock_social_media_posts.csv"
            df.to_csv(csv_file, index=False)
            
            logger.info(f"Created {len(posts)} mock social media posts")
            logger.info(f"Saved to {csv_file}")
            return df
            
        except Exception as e:
            logger.error(f"Error creating mock social media data: {e}")
            return None
    
    def process_social_media_data(self, df):
        """Process social media data into analytics-ready format"""
        logger.info("Processing social media data for analytics...")
        
        try:
            # Add temporal features
            df['post_date'] = pd.to_datetime(df['post_date'])
            df['year'] = df['post_date'].dt.year
            df['month'] = df['post_date'].dt.month
            df['day_of_week'] = df['post_date'].dt.day_name()
            df['hour'] = df['post_date'].dt.hour
            
            # Create urgency score based on sentiment and engagement
            df['urgency_score'] = (
                (df['engagement_score'] / df['engagement_score'].max()) * 0.4 +
                (abs(df['sentiment_polarity']) * 0.3) +
                (df['sentiment_subjectivity'] * 0.3)
            )
            
            # Classify urgency levels
            df['urgency_level'] = pd.cut(
                df['urgency_score'],
                bins=[0, 0.33, 0.66, 1.0],
                labels=['LOW', 'MODERATE', 'HIGH'],
                include_lowest=True
            )
            
            # Extract keywords and topics
            df['health_mentions'] = df['text'].str.lower().str.contains('|'.join(self.health_keywords))
            df['flood_mentions'] = df['text'].str.lower().str.contains('|'.join(self.flood_keywords))
            df['environmental_mentions'] = df['text'].str.lower().str.contains('|'.join(self.environmental_keywords))
            
            # Add metadata
            df['data_source'] = 'SOCIAL_MEDIA_NARRATIVES'
            df['ingestion_date'] = datetime.now().isoformat()
            df['processing_version'] = '1.0'
            
            logger.info(f"Processed social media data summary:")
            logger.info(f"Total posts: {len(df)}")
            logger.info(f"Category distribution:")
            logger.info(df['category'].value_counts())
            logger.info(f"Borough distribution:")
            logger.info(df['borough'].value_counts())
            logger.info(f"Sentiment distribution:")
            logger.info(df['sentiment_label'].value_counts())
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing social media data: {e}")
            return None
    
    def generate_narrative_insights(self, df):
        """Generate quantified insights from social media narratives"""
        logger.info("Generating narrative insights...")
        
        try:
            insights = []
            
            # Borough-level insights
            for borough in df['borough'].unique():
                borough_data = df[df['borough'] == borough]
                
                # Health concerns by borough
                health_posts = borough_data[borough_data['health_mentions']]
                if len(health_posts) > 0:
                    avg_sentiment = health_posts['sentiment_polarity'].mean()
                    total_engagement = health_posts['engagement_score'].sum()
                    
                    insights.append({
                        'insight_type': 'health_concern',
                        'geographic_area': borough,
                        'metric_name': 'social_health_sentiment',
                        'metric_value': round(avg_sentiment, 3),
                        'supporting_data': {
                            'post_count': len(health_posts),
                            'total_engagement': int(total_engagement),
                            'avg_engagement': round(health_posts['engagement_score'].mean(), 1)
                        },
                        'insight_date': datetime.now().isoformat()
                    })
                
                # Flood concerns by borough
                flood_posts = borough_data[borough_data['flood_mentions']]
                if len(flood_posts) > 0:
                    avg_urgency = flood_posts['urgency_score'].mean()
                    high_urgency_count = len(flood_posts[flood_posts['urgency_level'] == 'HIGH'])
                    
                    insights.append({
                        'insight_type': 'flood_concern',
                        'geographic_area': borough,
                        'metric_name': 'social_flood_urgency',
                        'metric_value': round(avg_urgency, 3),
                        'supporting_data': {
                            'post_count': len(flood_posts),
                            'high_urgency_posts': high_urgency_count,
                            'urgency_rate': round(high_urgency_count / len(flood_posts), 3)
                        },
                        'insight_date': datetime.now().isoformat()
                    })
            
            # Temporal insights
            recent_posts = df[df['post_date'] >= (datetime.now() - timedelta(days=30))]
            if len(recent_posts) > 0:
                # Trending concerns
                concern_trends = recent_posts.groupby(['category', 'borough']).agg({
                    'engagement_score': 'sum',
                    'post_id': 'count',
                    'sentiment_polarity': 'mean'
                }).reset_index()
                
                for _, trend in concern_trends.iterrows():
                    insights.append({
                        'insight_type': 'trending_concern',
                        'geographic_area': trend['borough'],
                        'metric_name': f"trend_{trend['category']}",
                        'metric_value': trend['engagement_score'],
                        'supporting_data': {
                            'post_count': trend['post_id'],
                            'avg_sentiment': round(trend['sentiment_polarity'], 3),
                            'time_period': '30_days'
                        },
                        'insight_date': datetime.now().isoformat()
                    })
            
            insights_df = pd.DataFrame(insights)
            logger.info(f"Generated {len(insights)} narrative insights")
            
            return insights_df
            
        except Exception as e:
            logger.error(f"Error generating narrative insights: {e}")
            return None
    
    def save_to_database(self, posts_df, insights_df):
        """Save social media data and insights to database"""
        logger.info("Saving social media data to database...")

        try:
            conn = sqlite3.connect(self.db_path)

            # Convert datetime columns to strings for SQLite compatibility
            posts_df_copy = posts_df.copy()
            posts_df_copy['post_date'] = posts_df_copy['post_date'].astype(str)

            # Convert any remaining datetime columns
            for col in posts_df_copy.columns:
                if posts_df_copy[col].dtype == 'datetime64[ns]':
                    posts_df_copy[col] = posts_df_copy[col].astype(str)

            # Save posts data
            posts_df_copy.to_sql('social_media_posts', conn, if_exists='replace', index=False)

            # Convert insights supporting_data to JSON string
            insights_df_copy = insights_df.copy()
            insights_df_copy['supporting_data'] = insights_df_copy['supporting_data'].apply(json.dumps)

            # Save insights data
            insights_df_copy.to_sql('social_media_insights', conn, if_exists='replace', index=False)
            
            # Create indexes
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_borough ON social_media_posts(borough)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_category ON social_media_posts(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_date ON social_media_posts(post_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_type ON social_media_insights(insight_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_area ON social_media_insights(geographic_area)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(posts_df)} posts and {len(insights_df)} insights to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def generate_dashboard_metrics(self, posts_df, insights_df):
        """Generate metrics for dashboard display"""
        logger.info("Generating dashboard metrics...")
        
        try:
            # Overall metrics
            total_posts = len(posts_df)
            total_engagement = posts_df['engagement_score'].sum()
            avg_sentiment = posts_df['sentiment_polarity'].mean()
            
            # Category breakdown
            category_stats = posts_df.groupby('category').agg({
                'post_id': 'count',
                'engagement_score': 'sum',
                'sentiment_polarity': 'mean',
                'urgency_score': 'mean'
            }).round(3)
            
            # Borough breakdown
            borough_stats = posts_df.groupby('borough').agg({
                'post_id': 'count',
                'engagement_score': 'sum',
                'sentiment_polarity': 'mean',
                'urgency_score': 'mean'
            }).round(3)
            
            # Temporal trends
            daily_trends = posts_df.groupby(posts_df['post_date'].dt.date).agg({
                'post_id': 'count',
                'engagement_score': 'sum',
                'sentiment_polarity': 'mean'
            }).tail(30)  # Last 30 days
            
            dashboard_metrics = {
                'overview': {
                    'total_posts': total_posts,
                    'total_engagement': int(total_engagement),
                    'avg_sentiment': round(avg_sentiment, 3),
                    'data_timespan': f"{posts_df['post_date'].min().date()} to {posts_df['post_date'].max().date()}"
                },
                'by_category': category_stats.to_dict(),
                'by_borough': borough_stats.to_dict(),
                'daily_trends': daily_trends.to_dict(),
                'top_concerns': insights_df.nlargest(10, 'metric_value')[['insight_type', 'geographic_area', 'metric_value']].to_dict('records')
            }
            
            logger.info("=== SOCIAL MEDIA DASHBOARD METRICS ===")
            logger.info(f"Total posts analyzed: {total_posts}")
            logger.info(f"Total community engagement: {int(total_engagement):,}")
            logger.info(f"Average sentiment: {round(avg_sentiment, 3)}")
            logger.info(f"Top concern categories: {category_stats.index.tolist()}")
            
            return dashboard_metrics
            
        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {e}")
            return None

def main():
    """Main execution function"""
    logger.info("Starting Social Media Narrative Integration for N2N Hackathon...")
    
    processor = SocialMediaNarrativeProcessor()
    
    # Create mock social media data (in real implementation, this would connect to APIs)
    posts_df = processor.create_mock_social_media_data(1000)
    
    if posts_df is not None:
        # Process the data
        processed_df = processor.process_social_media_data(posts_df)
        
        if processed_df is not None:
            # Generate insights
            insights_df = processor.generate_narrative_insights(processed_df)
            
            if insights_df is not None:
                # Save to database
                success = processor.save_to_database(processed_df, insights_df)
                
                if success:
                    # Generate dashboard metrics
                    dashboard_metrics = processor.generate_dashboard_metrics(processed_df, insights_df)
                    
                    if dashboard_metrics:
                        logger.info("✅ Social media narrative integration completed successfully!")
                        logger.info("📱 Community voices converted to quantified insights")
                        logger.info("🎯 Ready for 'Narrative 2 Numbers' demo!")
                        
                        return processed_df, insights_df, dashboard_metrics
                    else:
                        logger.error("Failed to generate dashboard metrics")
                else:
                    logger.error("Failed to save social media data to database")
            else:
                logger.error("Failed to generate insights")
        else:
            logger.error("Failed to process social media data")
    else:
        logger.error("Failed to create social media data")
    
    return None, None, None

if __name__ == "__main__":
    posts_data, insights_data, metrics = main()
