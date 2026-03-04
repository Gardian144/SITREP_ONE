import requests
import json
from datetime import datetime

# Configuration
EXTENT = "25,10,65,45" # Zone élargie
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    lat, lon = float(lat), float(lon)
    if 29.0 < lat < 34.0 and 34.0 < lon < 37.0: return "ISRAËL / PALESTINE"
    if 12.0 < lat < 20.0 and 37.0 < lon < 55.0: return "YÉMEN / MER ROUGE"
    if 33.0 < lat < 37.0 and 35.0 < lon < 45.0: return "SYRIE / LIBAN"
    return "ZONE MOYEN-ORIENT"

def fetch_nasa_alerts():
    # Test avec VIIRS d'abord, puis MODIS si vide
    satellites = ["VIIRS_SNPP_NRT", "MODIS_NRT"]
    all_events = []

    for sat in satellites:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{sat}/{EXTENT}/1"
        try:
            r = requests.get(url, timeout=15)
            lines = r.text.strip().split('\n')
            if len(lines) > 1:
                # On a trouvé des données !
                for line in lines[1:100]:
                    cols = line.split(',')
                    if len(cols) < 7: continue
                    all_events.append({
                        "id": cols[5],
                        "time": f"{cols[6][:2]}:{cols[6][2:]}",
                        "lat": float(cols[0]),
                        "lng": float(cols[1]),
                        "title": get_location_label(cols[0], cols[1]),
                        "is_hotspot": False # On calculera la densité après
                    })
                break # On s'arrête dès qu'on a des données
        except: continue

    # Calcul de densité (Hotspots)
    for ev in all_events:
        nearby = sum(1 for other in all_events if abs(other['lat'] - ev['lat']) < 0.2)
        if nearby > 4: ev['is_hotspot'] = True

    return all_events

def get_navy_dynamic():
    target = datetime(2026, 3, 14)
    today = datetime.now()
    diff = (target - today).days
    
    # Simulation trajet Charles de Gaulle
    if diff <= 0:
        lat, lng, status = 34.5, 32.5, "DÉPLOYÉ"
    else:
        prog = max(0, min(1, (10 - diff) / 10))
        lat = 55.0 - (prog * 20.5)
        lng = 5.0 + (prog * 27.5)
        status = f"TRANSIT (J-{diff})"

    return [
        {"name": "Charles de Gaulle (R91)", "lat": lat, "lng": lng, "type": "Porte-avions", "status": status},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate", "status": "MISSION MER ROUGE"}
    ]

# Export
data = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": fetch_nasa_alerts(),
    "navy": get_navy_dynamic()
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Update OK : {len(data['recent'])} alertes détectées.")
