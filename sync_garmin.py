#!/usr/bin/env python3
"""
HEWS - Garmin Sync for GitHub Actions (Enhanced)
Fetches comprehensive health data and saves as JSON for Obsidian plugin.
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
        # Vital Signs
        "hrv": None, "rhr": None, "stressAvg": None, "respiration": None,
        # Sleep
        "sleepDuration": None, "sleepDeep": None, "sleepLight": None,
        "sleepRem": None, "sleepAwake": None, "sleepScore": None,
        "sleepInterruptions": None,
        # Activity
        "steps": None, "floors": None, "intensityMinutes": None,
        "intensityMinutesModerate": None, "intensityMinutesVigorous": None,
        # Body Composition
        "weight": None, "bmi": None, "bodyFat": None, "muscleMass": None,
        "boneMass": None, "bodyWater": None,
        # Advanced Metrics
        "bodyBatteryStart": None, "bodyBatteryEnd": None, "bodyBatteryCharged": None,
        "spo2Avg": None, "spo2Min": None, "spo2Max": None,
        "hydration": None,
        "vo2Max": None, "fitnessAge": None,
        # Blood Pressure
        "systolicBp": None, "diastolicBp": None, "pulseBp": None,
        # Activities
        "activities": []
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
            health_data["intensityMinutesModerate"] = moderate
            health_data["intensityMinutesVigorous"] = vigorous
            health_data["intensityMinutes"] = moderate + (vigorous * 2)
            print(f"  ✓ Stats: RHR={health_data['rhr']}, Steps={health_data['steps']}")
    except Exception as e:
        print(f"  ✗ Error stats: {e}")
    
    # HRV
    try:
        hrv_data = client.get_hrv_data(date_str)
        if hrv_data and "hrvSummary" in hrv_data:
            health_data["hrv"] = hrv_data["hrvSummary"].get("lastNightAvg") or hrv_data["hrvSummary"].get("weeklyAvg")
            print(f"  ✓ HRV: {health_data['hrv']}")
    except Exception as e:
        print(f"  ✗ Error HRV: {e}")
    
    # Stress
    try:
        stress = client.get_stress_data(date_str)
        if stress and "avgStressLevel" in stress:
            health_data["stressAvg"] = stress["avgStressLevel"]
            print(f"  ✓ Stress: {health_data['stressAvg']}")
    except Exception as e:
        print(f"  ✗ Error stress: {e}")
    
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
            print(f"  ✓ Sleep: {health_data['sleepDuration']}min, Score={health_data['sleepScore']}")
    except Exception as e:
        print(f"  ✗ Error sleep: {e}")
    
    # Respiration
    try:
        respiration = client.get_respiration_data(date_str)
        if respiration:
            health_data["respiration"] = respiration.get("avgWakingRespirationValue")
            print(f"  ✓ Respiration: {health_data['respiration']}")
    except Exception as e:
        print(f"  ✗ Error respiration: {e}")

    # Body Composition - Primary Method
    try:
        body = client.get_body_composition(date_str)
        if body and body.get("weight"):
            health_data["weight"] = round(body["weight"] / 1000, 1)
            health_data["bmi"] = body.get("bmi")
            health_data["bodyFat"] = body.get("bodyFat")
            health_data["muscleMass"] = body.get("muscleMass")
            health_data["boneMass"] = body.get("boneMass")
            health_data["bodyWater"] = body.get("bodyWater")
            print(f"  ✓ Body Composition: Weight={health_data['weight']}kg, BMI={health_data['bmi']}")
    except Exception as e:
        print(f"  ✗ Error body composition: {e}")
    
    # Body Composition - Fallback Method (more reliable for weight)
    if health_data["weight"] is None:
        try:
            day_before = (target_date - timedelta(days=1)).strftime("%Y-%m-%d")
            day_after = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
            weigh_ins = client.get_weigh_ins(day_before, day_after)
            if weigh_ins and isinstance(weigh_ins, list):
                for weigh_in in weigh_ins:
                    if not isinstance(weigh_in, dict):
                        continue
                    if weigh_in.get("date", "").startswith(date_str):
                        weight_grams = weigh_in.get("weight")
                        if weight_grams:
                            health_data["weight"] = round(weight_grams / 1000, 1)
                            health_data["bmi"] = weigh_in.get("bmi")
                            health_data["bodyFat"] = weigh_in.get("bodyFat")
                            print(f"  ✓ Weight (fallback): {health_data['weight']}kg")
                            break
        except Exception as e:
            print(f"  ✗ Error weigh-ins fallback: {e}")
    
    # Body Composition - Second Fallback: get_daily_weigh_ins
    if health_data["weight"] is None:
        try:
            daily_weigh = client.get_daily_weigh_ins(date_str)
            if daily_weigh:
                entries = daily_weigh if isinstance(daily_weigh, list) else daily_weigh.get("dateWeightList", [])
                for entry in entries:
                    w = entry.get("weight")
                    if w:
                        health_data["weight"] = round(w / 1000, 1)
                        health_data["bmi"] = entry.get("bmi")
                        health_data["bodyFat"] = entry.get("bodyFat")
                        print(f"  ✓ Weight (daily weigh-ins): {health_data['weight']}kg")
                        break
        except Exception as e:
            print(f"  ✗ Error daily weigh-ins: {e}")

    # Blood Pressure
    try:
        bp_data = client.get_blood_pressure(date_str, date_str)
        if bp_data and isinstance(bp_data, dict):
            summaries = bp_data.get("measurementSummaries", [])
            if summaries and isinstance(summaries, list):
                summary = summaries[-1]
                measurements = summary.get("measurements", [])
                if measurements and isinstance(measurements, list):
                    m = measurements[-1]
                    health_data["systolicBp"] = m.get("systolic")
                    health_data["diastolicBp"] = m.get("diastolic")
                    health_data["pulseBp"] = m.get("pulse")
                    print(f"  ✓ Blood Pressure: {health_data['systolicBp']}/{health_data['diastolicBp']} mmHg, Pulse={health_data['pulseBp']}")
                else:
                    health_data["systolicBp"] = summary.get("highSystolic")
                    health_data["diastolicBp"] = summary.get("highDiastolic")
                    print(f"  ✓ Blood Pressure (summary): {health_data['systolicBp']}/{health_data['diastolicBp']} mmHg")
    except Exception as e:
        print(f"  ✗ Error blood pressure: {e}")

    # Body Battery
    try:
        # Body Battery needs date range
        day_before = (target_date - timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
        body_battery = client.get_body_battery(day_before, day_after)
        
        if body_battery and len(body_battery) > 0:
            # Find data for target date
            for bb in body_battery:
                if bb.get("date", "").startswith(date_str):
                    health_data["bodyBatteryStart"] = bb.get("startTimestampGMT")
                    health_data["bodyBatteryEnd"] = bb.get("endTimestampGMT")
                    health_data["bodyBatteryCharged"] = bb.get("charged")
                    print(f"  ✓ Body Battery: Charged={health_data['bodyBatteryCharged']}")
                    break
    except Exception as e:
        print(f"  ✗ Error body battery: {e}")
    
    # SpO2 (Blood Oxygen)
    try:
        spo2_data = client.get_spo2_data(date_str)
        if spo2_data:
            values = spo2_data.get("values", [])
            if values:
                spo2_readings = [v for v in values if v is not None]
                if spo2_readings:
                    health_data["spo2Avg"] = round(sum(spo2_readings) / len(spo2_readings), 1)
                    health_data["spo2Min"] = min(spo2_readings)
                    health_data["spo2Max"] = max(spo2_readings)
                    print(f"  ✓ SpO2: Avg={health_data['spo2Avg']}%, Min={health_data['spo2Min']}%")
    except Exception as e:
        print(f"  ✗ Error SpO2: {e}")
    
    # Hydration
    try:
        hydration_data = client.get_hydration_data(date_str)
        if hydration_data:
            health_data["hydration"] = hydration_data.get("valueInML")
            if health_data["hydration"]:
                print(f"  ✓ Hydration: {health_data['hydration']}ml")
    except Exception as e:
        print(f"  ✗ Error hydration: {e}")
    
    # Max Metrics (VO2 Max, Fitness Age)
    try:
        max_metrics = client.get_max_metrics(date_str)
        if max_metrics:
            vo2_max_data = max_metrics.get("vo2Max")
            if vo2_max_data:
                health_data["vo2Max"] = vo2_max_data.get("generic", {}).get("value")
            
            fitness_age_data = max_metrics.get("fitnessAge")
            if fitness_age_data:
                health_data["fitnessAge"] = fitness_age_data.get("value")
            
            if health_data["vo2Max"] or health_data["fitnessAge"]:
                print(f"  ✓ Max Metrics: VO2Max={health_data['vo2Max']}, FitnessAge={health_data['fitnessAge']}")
    except Exception as e:
        print(f"  ✗ Error max metrics: {e}")
    
    # Activities for the date
    try:
        activities_data = client.get_activities_fordate(date_str)
        if activities_data:
            activities_list = []
            for activity in activities_data:
                # Extract key statistics
                activity_type = activity.get("activityType")
                if isinstance(activity_type, dict):
                    activity_type = activity_type.get("typeKey")
                elif not isinstance(activity_type, str):
                    activity_type = str(activity_type) if activity_type else None
                activity_summary = {
                    "activityId": activity.get("activityId"),
                    "activityName": activity.get("activityName"),
                    "activityType": activity_type,
                    "startTimeLocal": activity.get("startTimeLocal"),
                    "duration": activity.get("duration"),  # in seconds
                    "distance": round(activity.get("distance", 0) / 1000, 2) if activity.get("distance") else None,  # Convert meters to km
                    "calories": activity.get("calories"),
                    "averageHR": activity.get("averageHR"),
                    "maxHR": activity.get("maxHR"),
                    "elevationGain": activity.get("elevationGain"),
                    "elevationLoss": activity.get("elevationLoss"),
                    "avgSpeed": round(activity.get("averageSpeed", 0) * 3.6, 2) if activity.get("averageSpeed") else None,  # m/s to km/h
                    "maxSpeed": round(activity.get("maxSpeed", 0) * 3.6, 2) if activity.get("maxSpeed") else None,
                    "steps": activity.get("steps"),
                    "avgPower": activity.get("avgPower"),
                    "maxPower": activity.get("maxPower"),
                    "trainingEffect": activity.get("aerobicTrainingEffect"),
                    "anaerobicEffect": activity.get("anaerobicTrainingEffect")
                }
                activities_list.append(activity_summary)
            
            health_data["activities"] = activities_list
            print(f"  ✓ Activities: {len(activities_list)} found")
            for act in activities_list:
                duration_min = act["duration"] // 60 if act["duration"] else 0
                print(f"    - {act['activityType']}: {duration_min}min, {act['distance']}km, {act['calories']}kcal")
    except Exception as e:
        print(f"  ✗ Error activities: {e}")
    
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
    print("HEWS Garmin Sync (Enhanced) - GitHub Actions")
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
