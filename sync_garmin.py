#!/usr/bin/env python3
"""
HEWS - Garmin Sync for GitHub Actions
Fetches health data and saves as JSON for Obsidian plugin.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from garminconnect import Garmin
except ImportError:
    print("ERROR: 'garminconnect' not installed!")
    exit(1)


def get_date_string(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def fetch_health_data(client: Garmin, target_date: datetime) -> dict:
    date_str = get_date_string(target_date)
    print(f"Fetching health data for {date_str}...")
    
    health_data = {
        "date": date_str,
        "source": "garmin",
        "fetchedAt": datetime.now().isoformat(),
        "hrv": None, "rhr": None, "stressAvg": None, "respiration": None,
        "sleepDuration": None, "sleepDeep": None, "sleepLight": None,
        "sleepRem": None, "sleepAwake": None, "sleepScore": None,
        "sleepInterruptions": None,
        "steps": None, "floors": None, "intensityMinutes": None,
        "weight": None, "bmi": None, "bodyFat": None
    }
    
    # Stats Summary
    try:
        stats = client.get_stats(date_str)
        if stats:
            health_data["rhr"] = stats.get("restingHeartRate")
            health_data["steps"] = stats.get("totalSteps")
            health_data["floors"] = stats.get("floorsClimbed")
            moderate = stats.get("moderateIntensityMinutes") or 0
            vigorous = stats.get("vigorousIntensityMinutes") or 0
            health_data["intensityMinutes"] = moderate + (vigorous * 2)
    except Exception as e:
        print(f"Error stats: {e}")
    
    # HRV
    try:
        hrv_data = client.get_hrv_data(date_str)
        if hrv_data and "hrvSummary" in hrv_data:
            health_data["hrv"] = hrv_data["hrvSummary"].get("lastNightAvg") or hrv_data["hrvSummary"].get("weeklyAvg")
    except Exception as e:
        print(f"Error HRV: {e}")
    
    # Stress
    try:
        stress = client.get_stress_data(date_str)
        if stress and "avgStressLevel" in stress:
            health_data["stressAvg"] = stress["avgStressLevel"]
    except Exception as e:
        print(f"Error stress: {e}")
    
    # Sleep
    try:
        sleep = client.get_sleep_data(date_str)
        if sleep and "dailySleepDTO" in sleep:
            s = sleep["dailySleepDTO"]
            if s.get("sleepTimeSeconds"):
                health_data["sleepDuration"] = s["sleepTimeSeconds"] // 60
            health_data["sleepDeep"] = (s.get("deepSleepSeconds") or 0) // 60
            health_data["sleepLight"] = (s.get("lightSleepSeconds") or 0) // 60
            health_data["sleepRem"] = (s.get("remSleepSeconds") or 0) // 60
            health_data["sleepAwake"] = (s.get("awakeSleepSeconds") or 0) // 60
            health_data["sleepInterruptions"] = s.get("awakeCount")
            if "sleepScores" in s:
                scores = s["sleepScores"]
                if isinstance(scores, dict):
                    health_data["sleepScore"] = scores.get("overall", {}).get("value") or scores.get("overallScore")
    except Exception as e:
        print(f"Error sleep: {e}")
    
    # Respiration
    try:
        respiration = client.get_respiration_data(date_str)
        if respiration:
            health_data["respiration"] = respiration.get("avgWakingRespirationValue")
    except Exception as e:
        print(f"Error respiration: {e}")

    # Body Composition
    try:
        body = client.get_body_composition(date_str)
        if body and body.get("weight"):
            health_data["weight"] = round(body["weight"] / 1000, 1)
            health_data["bmi"] = body.get("bmi")
            health_data["bodyFat"] = body.get("bodyFat")
    except Exception as e:
        print(f"Error body: {e}")
    
    return health_data


def main():
    # Get credentials from environment variables
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    
    if not email or not password:
        print("ERROR: GARMIN_EMAIL and GARMIN_PASSWORD environment variables required")
        exit(1)
    
    # Check for date range parameters (historical mode)
    start_date_str = os.environ.get("START_DATE")
    end_date_str = os.environ.get("END_DATE")
    
    print("=" * 50)
    print("HEWS Garmin Sync (GitHub Actions)")
    print("=" * 50)
    
    # Login to Garmin
    print("\nLogging in to Garmin Connect...")
    try:
        client = Garmin(email, password)
        client.login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        exit(1)
    
    # Determine mode
    if start_date_str and end_date_str:
        # Historical mode
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        print(f"\n📅 Historical mode: {start_date_str} to {end_date_str}")
        
        history = []
        current_date = start_date
        
        while current_date <= end_date:
            data = fetch_health_data(client, current_date)
            history.append(data)
            current_date += timedelta(days=1)
        
        output = {
            "lastSync": datetime.now().isoformat(),
            "mode": "historical",
            "startDate": start_date_str,
            "endDate": end_date_str,
            "today": None,
            "yesterday": None,
            "history": history
        }
        
        print(f"\n✓ Fetched {len(history)} days of data")
        
    else:
        # Normal daily mode
        print("\n📅 Normal mode: today + yesterday")
        
        today = datetime.now()
        today_data = fetch_health_data(client, today)
        
        yesterday = today - timedelta(days=1)
        yesterday_data = fetch_health_data(client, yesterday)
        
        output = {
            "lastSync": datetime.now().isoformat(),
            "mode": "daily",
            "today": today_data,
            "yesterday": yesterday_data,
            "history": []
        }
    
    # Save to JSON file
    output_path = Path("data/health_data.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 50)
    print(f"✓ Data saved to {output_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
