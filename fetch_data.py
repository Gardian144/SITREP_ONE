import requests
import json
from datetime import datetime

# Configuration
EXTENT = "30,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    lat, lon = float(lat), float(lon)
    if 29.5 < lat < 33.5 and 34.2 < lon < 36.5: return "ISRAËL / PALESTINE"
    if 35.5 < lat < 36.5 and 51.0 < lon < 52.0: return "SECTEUR TÉHÉRAN"
    if 12.0 < lat < 20.0 and 38.0 < lon < 45.0: return "MER ROUGE / YÉMEN"
    if 24.0 < lat < 30.0 and 48.0 < lon < 56.0: return "GOLFE ARABO-PERSIQUE"
    return "ZONE MOYEN-ORIENT"

def fetch_nasa_alerts():
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    try:
        response = requests.get(url, timeout=20)
        lines = response.text.strip().split('\n')
        if len(lines) <= 1: return [] 

        raw_events = []
        # On lit les 30 derniers points
        for line in lines[1:31]: 
            cols = line.split(',')
            if len(cols) < 7: continue
            raw_events.append({
                "lat": float(cols[0]), 
                "lng": float(cols[1]), 
                "time": f"{cols[6][:2]}:{cols[6][2:]}",
                "id": cols[5]
            })

        processed_alerts = []
        for e in raw_events:
            # Calcul de densité : combien de points dans un rayon de 0.5 degré ?
            density = sum(1 for other in raw_events if abs(other['lat'] - e['lat']) < 0.5 and abs(other['lng'] - e['lng']) < 0.5)
            
            location = get_location_label(e['lat'], e['lng'])
            is_hotspot = density > 3 # Seuil pour déclencher l'alerte Hotspot
            
            processed_alerts.append({
                "id": f"nasa_{e['id']}_{e['lat']}",
                "time": e['time'],
                "lat": e['lat'],
                "lng": e['lng'],
                "title": f"⚠️ HOTSPOT : {location}" if is_hotspot else f"FRAPPE : {location}",
                "type": "HOTSPOT" if is_hotspot else "STRIKE"
            })
        
        return processed_alerts
    except Exception as e:
        print(f"Erreur : {e}")
        return []

# Run
alerts = fetch_nasa_alerts()
if alerts:
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    print(f"OK : {len(alerts)} alertes générées.")
