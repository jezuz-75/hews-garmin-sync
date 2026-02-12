# HEWS Garmin Sync

Automatischer täglicher Import von umfassenden Garmin Connect Gesundheits- und Aktivitätsdaten.

## ✨ Features

### 📊 Gesundheitsdaten
- **Vitaldaten:** HRV, Ruhepuls, Stress, Atmung
- **Schlaf:** Dauer, Phasen (Tief/REM/Leicht), Score, Unterbrechungen
- **Aktivität:** Schritte, Etagen, Intensitätsminuten (moderat/vigorous)
- **Körper:** Gewicht, BMI, Körperfett, Muskelmasse, Knochenmasse, Körperwasser
- **Advanced:** Body Battery, SpO2, Hydration, VO2 Max, Fitness Age

### 🏃 Aktivitäten-Tracking
- **Alle täglichen Aktivitäten** (Laufen, Radfahren, Schwimmen, etc.)
- **Detaillierte Statistiken:** Dauer, Distanz, Kalorien, HR, Geschwindigkeit, Höhenmeter
- **Trainingseffekte:** Aerob & Anaerob
- Siehe [ACTIVITIES_REFERENCE.md](ACTIVITIES_REFERENCE.md) für Details

## Setup

1. **Repository Secrets konfigurieren:**
   - Gehe zu Settings → Secrets and variables → Actions
   - Klicke "New repository secret"
   - Erstelle:
     - `GARMIN_EMAIL` - Deine Garmin E-Mail
     - `GARMIN_PASSWORD` - Dein Garmin Passwort

2. **Ersten Sync manuell starten:**
   - Gehe zu Actions → Daily Garmin Sync → Run workflow

## Dateien

| Datei | Beschreibung |
|-------|--------------|
| `sync_garmin.py` | Python-Script für Datenabruf (Enhanced) |
| `requirements.txt` | Python Dependencies |
| `.github/workflows/daily-sync.yml` | GitHub Actions Zeitplan |
| `data/health_data.json` | Aktuelle Gesundheitsdaten |
| `ACTIVITIES_REFERENCE.md` | Dokumentation Aktivitäts-Daten |

## Zeitplan

Der Sync läuft täglich um **7:10 Uhr MEZ** (6:10 UTC).

## Für Obsidian Plugin

Das Plugin liest die Datei:
```
https://raw.githubusercontent.com/jezuz-75/hews-garmin-sync/main/data/health_data.json
```

## Verfügbare Datenfelder (27 Gesundheitsmetriken + Aktivitäten)

**Vitaldaten:** `hrv`, `rhr`, `stressAvg`, `respiration`  
**Schlaf:** `sleepDuration`, `sleepDeep`, `sleepLight`, `sleepRem`, `sleepAwake`, `sleepScore`, `sleepInterruptions`  
**Aktivität:** `steps`, `floors`, `intensityMinutes`, `intensityMinutesModerate`, `intensityMinutesVigorous`  
**Körper:** `weight`, `bmi`, `bodyFat`, `muscleMass`, `boneMass`, `bodyWater`  
**Advanced:** `bodyBatteryStart`, `bodyBatteryEnd`, `bodyBatteryCharged`, `spo2Avg`, `spo2Min`, `spo2Max`, `hydration`, `vo2Max`, `fitnessAge`  
**Aktivitäten:** `activities[]` (Array mit allen Aktivitäten des Tages)
