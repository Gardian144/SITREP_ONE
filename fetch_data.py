import requests, json
from datetime import datetime

# NASA Config
MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def get_data():
    # NASA Alerts
    events = []
    try:
        r = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1", timeout=10)
        lines = r.text.strip().split('\n')
        if len(lines) > 1:
            for line in lines[1:31]:
                cols = line.split(',')
                events.append({"lat": float(cols[0]), "lng": float(cols[1]), "t": cols[6]})
    except: pass

    # France Assets (Positions fixes et dynamiques)
    return {
        "last": datetime.now().strftime("%H:%M"),
        "alerts": events,
        "units": [
            {"n": "Charles de Gaulle (R91)", "lat": 48.5, "lng": -5.0, "type": "Porte-avions", "s": "EN TRANSIT"},
            {"n": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate", "s": "POSTÉ"}
        ],
        "bases": [
            {"n": "BAP JORDANIE", "lat": 32.15, "lng": 36.10, "i": "6x Rafale"},
            {"n": "FFDJ DJIBOUTI", "lat": 11.58, "lng": 43.14, "i": "Forces Prépositionnées"}
        ]
    }

with open('data.json', 'w') as f:
    json.dump(get_data(), f)
