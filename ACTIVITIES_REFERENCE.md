# Garmin Activities - Verfügbare Daten

## Übersicht

Das Script ruft nun **alle Aktivitäten des jeweiligen Tages** ab und speichert diese im JSON.

## Verfügbare Aktivitäts-Felder

| Feld | Beschreibung | Beispiel | Einheit |
|------|--------------|----------|---------|
| `activityId` | Eindeutige ID der Aktivität | `12345678901` | - |
| `activityName` | Name der Aktivität | `"Morgenlauf"` | - |
| `activityType` | Typ der Aktivität | `"running"`, `"cycling"`, `"swimming"` | - |
| `startTimeLocal` | Startzeit (lokal) | `"2026-02-09 07:30:00"` | - |
| `duration` | Dauer | `3600` | Sekunden |
| `distance` | Distanz | `5.2` | Kilometer |
| `calories` | Verbrannte Kalorien | `450` | kcal |
| `averageHR` | Durchschnittliche Herzfrequenz | `145` | bpm |
| `maxHR` | Maximale Herzfrequenz | `178` | bpm |
| `elevationGain` | Höhenmeter bergauf | `120` | Meter |
| `elevationLoss` | Höhenmeter bergab | `115` | Meter |
| `avgSpeed` | Durchschnittsgeschwindigkeit | `8.6` | km/h |
| `maxSpeed` | Höchstgeschwindigkeit | `12.3` | km/h |
| `steps` | Schritte (bei Laufaktivitäten) | `6800` | - |
| `avgPower` | Durchschnittsleistung | `220` | Watt |
| `maxPower` | Maximale Leistung | `380` | Watt |
| `trainingEffect` | Aerober Trainingseffekt | `3.2` | 0-5 |
| `anaerobicEffect` | Anaerober Trainingseffekt | `2.8` | 0-5 |

## Aktivitätstypen (Beispiele)

- `running` - Laufen
- `cycling` - Radfahren
- `walking` - Gehen
- `swimming` - Schwimmen
- `hiking` - Wandern
- `strength_training` - Krafttraining
- `yoga` - Yoga
- `cardio` - Cardio
- `elliptical` - Crosstrainer
- `indoor_cycling` - Indoor-Cycling

## JSON-Struktur

```json
{
  "date": "2026-02-09",
  "activities": [
    {
      "activityId": 12345678901,
      "activityName": "Morgenlauf",
      "activityType": "running",
      "startTimeLocal": "2026-02-09 07:30:00",
      "duration": 3600,
      "distance": 5.2,
      "calories": 450,
      "averageHR": 145,
      "maxHR": 178,
      "elevationGain": 120,
      "elevationLoss": 115,
      "avgSpeed": 8.6,
      "maxSpeed": 12.3,
      "steps": 6800,
      "avgPower": null,
      "maxPower": null,
      "trainingEffect": 3.2,
      "anaerobicEffect": 2.8
    }
  ]
}
```

## Verwendung in Obsidian

### Template-Platzhalter

Die Aktivitäten werden als Array im JSON gespeichert. Das Obsidian-Plugin muss diese verarbeiten und als Markdown-Liste darstellen.

**Beispiel-Output:**

```markdown
## 🏃 Aktivitäten (9.2.2026)

- **Morgenlauf** (running)
  - Dauer: 60 Min
  - Distanz: 5.2 km
  - Kalorien: 450 kcal
  - ⌀ HR: 145 bpm | Max: 178 bpm
  - ⌀ Speed: 8.6 km/h
  - Trainingseffekt: 3.2 (aerob) | 2.8 (anaerob)

- **Abendspaziergang** (walking)
  - Dauer: 30 Min
  - Distanz: 2.1 km
  - Kalorien: 120 kcal
```

## Hinweise

1. **Datum-Zuordnung:** Aktivitäten werden nach Startzeit dem entsprechenden Tag zugeordnet
2. **Leere Aktivitäten:** Wenn keine Aktivität an einem Tag stattfand, ist `activities` ein leeres Array `[]`
3. **Null-Werte:** Felder die nicht verfügbar sind (z.B. Leistung bei Lauf-Aktivitäten) werden als `null` gespeichert
4. **Einheiten:** Alle Einheiten sind automatisch konvertiert:
   - Distanz: Meter → Kilometer
   - Geschwindigkeit: m/s → km/h
   - Dauer: Sekunden (muss im Template zu Minuten umgerechnet werden)
