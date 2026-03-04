import requests, json
from datetime import datetime

MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def get_intel():
    # NASA Alerts
    alerts = []
    try:
        r = requests.get(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1", timeout=10)
        lines = r.text.strip().split('\n')
        for line in lines[1:25]:
            cols = line.split(',')
            alerts.append({"lat": float(cols[0]), "lng": float(cols[1]), "t": cols[6]})
    except: pass

    return {
        "update": datetime.now().strftime("%H:%M"),
        "alerts": alerts,
        "units": [
            {"n": "Charles de Gaulle (R91)", "lat": 48.8, "lng": -4.5, "s": "EN TRANSIT", "t": "Porte-avions"},
            {"n": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "s": "MISSION", "t": "Frégate"}
        ],
        "bases": [
            {"n": "BAP JORDANIE", "lat": 32.15, "lng": 36.1, "d": "6x Rafale"},
            {"n": "FFDJ DJIBOUTI", "lat": 11.58, "lng": 43.1, "d": "Base Stratégique"}
        ]
    }

with open('data.json', 'w') as f:
    json.dump(get_intel(), f)
