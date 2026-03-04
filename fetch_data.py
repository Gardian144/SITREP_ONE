import requests
import json
from datetime import datetime, timedelta

EXTENT = "30,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    lat, lon = float(lat), float(lon)
    if 29.5 < lat < 33.5 and 34.2 < lon < 36.5: return "ISRAËL / PALESTINE"
    if 35.5 < lat < 36.5 and 51.0 < lon < 52.0: return "SECTEUR TÉHÉRAN"
    if 12.0 < lat < 20.0 and 38.0 < lon < 45.0: return "MER ROUGE / YÉMEN"
    return "ZONE MOYEN-ORIENT"

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        response = requests.get(url, timeout=20)
        lines = response.text.strip().split('\n')
        if len(lines) <= 1: return [] 

        events = []
        for line in lines[1:51]: 
            cols = line.split(',')
            lat, lon = float(cols[0]), float(cols[1])
            # Calcul de densité pour les Hotspots
            nearby = sum(1 for l in lines[1:51] if abs(float(l.split(',')[0]) - lat) < 0.3)
            
            events.append({
                "id": cols[5],
                "time": f"{cols[6][:2]}:{cols[6][2:]}",
                "date": cols[5], # Date brute NASA
                "lat": lat,
                "lng": lon,
                "title": get_location_label(lat, lon),
                "is_hotspot": nearby > 3
            })
        return events
    except: return []

# Simulation de positions de navires militaires (Positions connues/publiques)
def get_navy():
    return [
        {"name": "Charles de Gaulle (R91)", "lat": 34.5, "lng": 20.2, "type": "Porte-avions"},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate"}
    ]

alerts = fetch_nasa_alerts()
navy = get_navy()

# Export structuré
output = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": alerts, # Dernières 24h
    "navy": navy
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
