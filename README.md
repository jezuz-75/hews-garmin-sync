# HEWS Garmin Sync

Automatischer täglicher Import von Garmin Connect Gesundheitsdaten.

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
| `sync_garmin.py` | Python-Script für Datenabruf |
| `requirements.txt` | Python Dependencies |
| `.github/workflows/daily-sync.yml` | GitHub Actions Zeitplan |
| `data/health_data.json` | Aktuelle Gesundheitsdaten |

## Zeitplan

Der Sync läuft täglich um **7:00 Uhr MEZ** (6:00 UTC).

## Für Obsidian Plugin

Das Plugin liest die Datei:
```
https://raw.githubusercontent.com/jezuz-75/hews-garmin-sync/main/data/health_data.json
```
