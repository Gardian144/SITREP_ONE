import requests
import json
from datetime import datetime

# Configuration
EXTENT = "20,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    lat, lon = float(lat), float(lon)
    if 29.0 < lat < 34.0 and 34.0 < lon < 37.0: return "ISRAËL / PALESTINE"
    if 12.0 < lat < 20.0 and 37.0 < lon < 55.0: return "YÉMEN / MER ROUGE"
    if 33.0 < lat < 37.0 and 35.0 < lon < 45.0: return "SYRIE / LIBAN"
    return "ZONE MOYEN-ORIENT"

def fetch_nasa_alerts():
    satellites = ["VIIRS_SNPP_NRT", "MODIS_NRT"]
    all_events = []
    for sat in satellites:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{sat}/{EXTENT}/1"
        try:
            r = requests.get(url, timeout=15)
            lines = r.text.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:100]:
                    cols = line.split(',')
                    if len(cols) < 7: continue
                    all_events.append({
                        "id": cols[5],
                        "time": f"{cols[6][:2]}:{cols[6][2:]}",
                        "lat": float(cols[0]), "lng": float(cols[1]),
                        "title": get_location_label(cols[0], cols[1]),
                        "is_hotspot": False
                    })
                break
        except: continue
    for ev in all_events:
        nearby = sum(1 for other in all_events if abs(other['lat'] - ev['lat']) < 0.2)
        if nearby > 4: ev['is_hotspot'] = True
    return all_events

def get_military_intel():
    return {
        "bases": [
            {"name": "Base Al-Udeid (USA)", "lat": 25.11, "lng": 51.21, "assets": "F-15E, KC-135", "side": "US"},
            {"name": "Base Hmeimim (RUS)", "lat": 35.40, "lng": 35.94, "assets": "Su-35, S-400", "side": "RU"},
            {"name": "Base Akrotiri (UK)", "lat": 34.59, "lng": 32.98, "assets": "Typhoon", "side": "UK"},
            {"name": "Base Nevatim (ISR)", "lat": 31.20, "lng": 35.01, "assets": "F-35I Adir", "side": "IL"},
            {"name": "Base Prince Sultan (SA)", "lat": 24.15, "lng": 47.58, "assets": "Patriot, F-15", "side": "SA"}
        ],
        "france": [
            {"name": "Base 188 Djibouti", "lat": 11.58, "lng": 43.14, "assets": "Mirage 2000-5D", "type": "AIR"},
            {"name": "Forces aux Emirats (FFEAU)", "lat": 24.48, "lng": 54.32, "assets": "Rafale F3R", "type": "MIXED"},
            {"name": "Base H5 (Jordanie)", "lat": 32.15, "lng": 36.10, "assets": "Rafale (Op. Chammal)", "type": "AIR"}
        ]
    }

def get_navy_dynamic():
    target = datetime(2026, 3, 14)
    today = datetime.now()
    diff = (target - today).days
    # Calcul position CdG
    prog = max(0, min(1, (10 - diff) / 10))
    cdg_lat = 55.0 - (prog * 20.5)
    cdg_lng = 5.0 + (prog * 27.5)
    
    return [
        {"name": "Charles de Gaulle (R91)", "lat": cdg_lat, "lng": cdg_lng, "type": "Porte-avions", "status": "TRANSIT" if diff > 0 else "OPS"},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate AA", "status": "MISSION MER ROUGE"}
    ]

data = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": fetch_nasa_alerts(),
    "navy": get_navy_dynamic(),
    "intel": get_military_intel()
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
