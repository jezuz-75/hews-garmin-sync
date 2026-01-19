"""
HEWS - Health Early Warning System
Garmin Connect Data Sync Script

Uses garminconnect library (more stable and feature-complete than garth)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from garminconnect import Garmin
except ImportError:
    print("ERROR: 'garminconnect' not installed!")
    print("Please run: pip install garminconnect")
    exit(1)


def get_date_string(date: datetime) -> str:
    """Format date as YYYY-MM-DD"""
    return date.strftime("%Y-%m-%d")


def fetch_health_data(client: Garmin, target_date: datetime) -> dict:
    """Fetch all health data for a specific date"""
    date_str = get_date_string(target_date)
    
    print(f"Fetching health data for {date_str}...")
    
    health_data = {
        "date": date_str,
        "source": "garmin",
        "fetchedAt": datetime.now().isoformat(),
        
        # Vital signs
        "hrv": None,
        "rhr": None,
        "stressAvg": None,
        "respiration": None,
        
        # Sleep
        "sleepDuration": None,
        "sleepDeep": None,
        "sleepLight": None,
        "sleepRem": None,
        "sleepAwake": None,
        "sleepScore": None,
        "sleepInterruptions": None,
        
        # Activity
        "steps": None,
        "floors": None,
        "intensityMinutes": None,
        "intensityMinutesModerate": None,
        "intensityMinutesVigorous": None,
        "calories": None,
        "activeCalories": None,
        
        # Body composition
        "weight": None,
        "bmi": None,
        "bodyFat": None,
        "muscleMass": None,
        "visceralFat": None,
        "bodyWater": None,
        "boneMass": None,
    }
    
    # === STATS SUMMARY (Steps, RHR, Floors, Intensity Minutes) ===
    try:
        stats = client.get_stats(date_str)
        if stats:
            health_data["rhr"] = stats.get("restingHeartRate")
            health_data["steps"] = stats.get("totalSteps")
            health_data["floors"] = stats.get("floorsClimbed")
            health_data["calories"] = stats.get("totalKilocalories")
            health_data["activeCalories"] = stats.get("activeKilocalories")
            
            moderate = stats.get("moderateIntensityMinutes") or 0
            vigorous = stats.get("vigorousIntensityMinutes") or 0
            health_data["intensityMinutesModerate"] = moderate
            health_data["intensityMinutesVigorous"] = vigorous
            health_data["intensityMinutes"] = moderate + (vigorous * 2)
            
            print(f"  ✓ Stats: {health_data['steps']} steps, RHR {health_data['rhr']} bpm")
    except Exception as e:
        print(f"  ✗ Failed to fetch stats: {e}")
    
    # === HRV DATA ===
    try:
        hrv_data = client.get_hrv_data(date_str)
        if hrv_data and "hrvSummary" in hrv_data:
            # Try lastNightAvg first, then weeklyAvg
            health_data["hrv"] = hrv_data["hrvSummary"].get("lastNightAvg") or hrv_data["hrvSummary"].get("weeklyAvg")
            print(f"  ✓ HRV: {health_data['hrv']} ms")
    except Exception as e:
        print(f"  ✗ Failed to fetch HRV: {e}")
    
    # === STRESS DATA ===
    try:
        stress = client.get_stress_data(date_str)
        if stress:
            health_data["stressAvg"] = stress.get("avgStressLevel")
            print(f"  ✓ Stress: {health_data['stressAvg']}")
    except Exception as e:
        print(f"  ✗ Failed to fetch stress: {e}")
    
    # === SLEEP DATA ===
    try:
        sleep = client.get_sleep_data(date_str)
        if sleep and "dailySleepDTO" in sleep:
            s = sleep["dailySleepDTO"]
            
            if s.get("sleepTimeSeconds"):
                health_data["sleepDuration"] = s["sleepTimeSeconds"] // 60
            if s.get("deepSleepSeconds"):
                health_data["sleepDeep"] = s["deepSleepSeconds"] // 60
            if s.get("lightSleepSeconds"):
                health_data["sleepLight"] = s["lightSleepSeconds"] // 60
            if s.get("remSleepSeconds"):
                health_data["sleepRem"] = s["remSleepSeconds"] // 60
            if s.get("awakeSleepSeconds"):
                health_data["sleepAwake"] = s["awakeSleepSeconds"] // 60
            
            health_data["sleepInterruptions"] = s.get("awakeCount")
            
            # Sleep Score
            if "sleepScores" in s:
                scores = s["sleepScores"]
                if isinstance(scores, dict):
                    if "overall" in scores:
                        health_data["sleepScore"] = scores["overall"].get("value")
                    elif "overallScore" in scores:
                        health_data["sleepScore"] = scores["overallScore"]
            
            print(f"  ✓ Sleep: {health_data['sleepDuration']} min, Score: {health_data['sleepScore']}")
    except Exception as e:
        print(f"  ✗ Failed to fetch sleep: {e}")
    
    # === RESPIRATION DATA ===
    try:
        respiration = client.get_respiration_data(date_str)
        if respiration:
            health_data["respiration"] = respiration.get("avgWakingRespirationValue") or respiration.get("avgSleepRespirationValue")
            print(f"  ✓ Respiration: {health_data['respiration']}")
    except Exception as e:
        print(f"  ✗ Failed to fetch respiration: {e}")
    
    # === BODY COMPOSITION ===
    try:
        body = client.get_body_composition(date_str)
        if body and body.get("weight"):
            health_data["weight"] = round(body["weight"] / 1000, 1)  # g to kg
            health_data["bmi"] = round(body.get("bmi", 0), 1) if body.get("bmi") else None
            health_data["bodyFat"] = round(body.get("bodyFat", 0), 1) if body.get("bodyFat") else None
            health_data["muscleMass"] = round(body.get("muscleMass", 0) / 1000, 1) if body.get("muscleMass") else None
            health_data["visceralFat"] = body.get("visceralFat")
            health_data["bodyWater"] = round(body.get("bodyWater", 0), 1) if body.get("bodyWater") else None
            health_data["boneMass"] = round(body.get("boneMass", 0) / 1000, 1) if body.get("boneMass") else None
            print(f"  ✓ Body: {health_data['weight']} kg")
    except Exception as e:
        print(f"  ✗ Failed to fetch body composition: {e}")
    
    return health_data


def main():
    # Get credentials from environment variables
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    
    if not email or not password:
        print("ERROR: GARMIN_EMAIL and GARMIN_PASSWORD environment variables required")
        exit(1)
    
    print("=" * 50)
    print("HEWS Garmin Sync (garminconnect)")
    print("=" * 50)
    
    # Login to Garmin Connect
    print("\nLogging in to Garmin Connect...")
    try:
        client = Garmin(email, password)
        client.login()
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        exit(1)
    
    # Fetch today's data
    today = datetime.now()
    today_data = fetch_health_data(client, today)
    
    # Fetch yesterday's data
    yesterday = today - timedelta(days=1)
    yesterday_data = fetch_health_data(client, yesterday)
    
    # Build output structure
    output = {
        "lastSync": datetime.now().isoformat(),
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
