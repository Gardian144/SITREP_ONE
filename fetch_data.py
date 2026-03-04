import requests
import json
from datetime import datetime

# Config NASA
EXTENT = "20,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def fetch_nasa():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')
        events = []
        if len(lines) > 1:
            for line in lines[1:50]:
                cols = line.split(',')
                events.append({
                    "lat": float(cols[0]), "lng": float(cols[1]),
                    "time": f"{cols[6][:2]}:{cols[6][2:]}",
                    "is_hotspot": False
                })
        return events
    except: return []

def get_navy():
    # Simulation trajet Charles de Gaulle (R91)
    target = datetime(2026, 3, 14)
    diff = (target - datetime.now()).days
    prog = max(0, min(1, (10 - diff) / 10))
    lat = 55.0 - (prog * 20.5)
    lng = 5.0 + (prog * 27.5)
    return [
        {"name": "Charles de Gaulle (R91)", "lat": lat, "lng": lng, "status": "TRANSIT"},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "status": "POSTÉ"}
    ]

# Création du JSON
data = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": fetch_nasa(),
    "navy": get_navy(),
    "bases": [
        {"name": "Base Al-Udeid (USA)", "lat": 25.11, "lng": 51.21, "info": "F-15E"},
        {"name": "Base Djibouti (FRA)", "lat": 11.58, "lng": 43.14, "info": "Mirage 2000"}
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print("Update OK")
