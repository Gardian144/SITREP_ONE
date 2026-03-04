import requests
import json
from datetime import datetime

MAP_KEY = "3a967f64858b76c839f9b5a805a50785"
EXTENT = "20,10,65,45"

def fetch_nasa():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        r = requests.get(url, timeout=15)
        lines = r.text.strip().split('\n')
        events = []
        if len(lines) > 1:
            for line in lines[1:30]: # On limite à 30 alertes
                cols = line.split(',')
                events.append({"lat": float(cols[0]), "lng": float(cols[1]), "time": cols[6]})
        return events
    except: return []

def get_navy():
    # Simulation trajet Charles de Gaulle vers Mer Rouge
    target = datetime(2026, 3, 14)
    diff = (target - datetime.now()).days
    prog = max(0, min(1, (10 - diff) / 10))
    # Depart Manche (50N, -2W) -> Arrivée Suez (30N, 32E)
    lat = 50.0 - (prog * 20.0)
    lng = -2.0 + (prog * 34.0)
    return [
        {"name": "Charles de Gaulle (R91)", "lat": lat, "lng": lng, "type": "Porte-avions", "status": f"TRANSIT (J-{diff})"},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate", "status": "MISSION MER ROUGE"}
    ]

data = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": fetch_nasa(),
    "navy": get_navy(),
    "bases": [
        {"name": "BAP Jordanie (Rafale)", "lat": 32.15, "lng": 36.10, "info": "6x Rafale déployés"},
        {"name": "FFDJ Djibouti", "lat": 11.58, "lng": 43.14, "info": "Base stratégique"},
        {"name": "Base Navale Abu Dhabi", "lat": 24.48, "lng": 54.32, "info": "Présence permanente"}
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
