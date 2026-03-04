import requests
import json
from datetime import datetime

MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def fetch_nasa():
    # On essaye deux sources satellite pour être sûr d'avoir des alertes
    satellites = ["VIIRS_SNPP_NRT", "MODIS_NRT"]
    events = []
    for sat in satellites:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{sat}/{EXTENT}/1"
        try:
            r = requests.get(url, timeout=15)
            lines = r.text.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:50]:
                    cols = line.split(',')
                    events.append({
                        "lat": float(cols[0]), 
                        "lng": float(cols[1]), 
                        "time": f"{cols[6][:2]}:{cols[6][2:]}",
                        "conf": cols[8]
                    })
                break # Si on a des données, on s'arrête là
        except: continue
    return events

def get_navy():
    target = datetime(2026, 3, 14)
    prog = max(0, min(1, (10 - (target - datetime.now()).days) / 10))
    return [
        {"name": "CDG (R91)", "lat": 50.0 - (prog * 20.0), "lng": -2.0 + (prog * 34.0), "type": "Porte-avions", "status": "OPS"},
        {"name": "FREMM ALSACE", "lat": 14.2, "lng": 42.8, "type": "Frégate AA", "status": "SURVEILLANCE"}
    ]

data = {
    "last_update": datetime.now().strftime("%H:%M:%S"),
    "recent": fetch_nasa(),
    "navy": get_navy(),
    "bases": [
        {"name": "BAP JORDANIE", "lat": 32.15, "lng": 36.10, "label": "RAFALE DETACHMENT"},
        {"name": "FFDJ DJIBOUTI", "lat": 11.58, "lng": 43.14, "label": "BASE STRATÉGIQUE"}
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
