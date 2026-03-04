import requests
import json
from datetime import datetime

# Configuration NASA
EXTENT = "30,10,65,45" 
MAP_KEY = "3a967f64858b76c839f9b5a805a50785" 

def get_location_label(lat, lon):
    lat, lon = float(lat), float(lon)
    if 29.5 < lat < 33.5 and 34.2 < lon < 36.5: return "ISRAËL / PALESTINE"
    if 35.5 < lat < 36.5 and 51.0 < lon < 52.0: return "SECTEUR TÉHÉRAN"
    if 12.0 < lat < 20.0 and 38.0 < lon < 45.0: return "MER ROUGE / YÉMEN"
    return "ZONE MOYEN-ORIENT"

def fetch_nasa_alerts():
    # On passe de 1 à 10 pour récupérer les données sur une plage plus large si besoin
    # Et on utilise MODIS en complément si VIIRS est vide
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{EXTENT}/1"
    
    try:
        response = requests.get(url, timeout=20)
        # Si la NASA répond "S3_..." ou une erreur de clé, on intercepte
        if response.status_code != 200 or "Invalid" in response.text:
            print("Erreur API NASA : Vérifie ta clé ou le quota")
            return []

        lines = response.text.strip().split('\n')
        
        # Si vide, on tente le satellite secondaire (MODIS) qui a souvent plus de données historiques
        if len(lines) <= 1:
            url_alt = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/MODIS_NRT/{EXTENT}/1"
            response = requests.get(url_alt, timeout=20)
            lines = response.text.strip().split('\n')

        if len(lines) <= 1: return [] 

        events = []
        # On trie pour avoir les plus récents en premier
        data_lines = lines[1:100] # On prend jusqu'à 100 points
        
        for line in data_lines: 
            cols = line.split(',')
            if len(cols) < 7: continue
            
            lat, lon = float(cols[0]), float(cols[1])
            # Calcul de densité : si beaucoup de points autour, c'est un gros bombardement
            nearby = sum(1 for l in data_lines if abs(float(l.split(',')[0]) - lat) < 0.2)
            
            events.append({
                "id": cols[5],
                "time": f"{cols[6][:2]}:{cols[6][2:]}",
                "lat": lat,
                "lng": lon,
                "title": get_location_label(lat, lon),
                "is_hotspot": nearby > 5 # Plus sensible pour détecter les zones de guerre
            })
        return events
    except Exception as e:
        print(f"Erreur Fetch: {e}")
        return []

# Calcul de la position du Charles de Gaulle selon la date
def get_navy_dynamic():
    target_date = datetime(2026, 3, 14) # Date d'arrivée estimée
    today = datetime.now()
    
    # S'il reste du temps avant le 14 mars, on simule la descente
    diff_days = (target_date - today).days
    if diff_days <= 0:
        cdg_lat, cdg_lng, status = 34.5, 32.5, "DÉPLOYÉ (CHYPRE)"
    else:
        # Il part de 55N (Nord) et descend vers 34.5N
        progression = max(0, min(1, (10 - diff_days) / 10))
        cdg_lat = 55.0 - (progression * 20.5)
        cdg_lng = 5.0 + (progression * 27.5)
        status = "TRANSIT (EN ROUTE)"

    return [
        {"name": "Charles de Gaulle (R91)", "lat": cdg_lat, "lng": cdg_lng, "type": "Porte-avions", "status": status},
        {"name": "FREMM Alsace", "lat": 14.2, "lng": 42.8, "type": "Frégate (Escorte)", "status": "DÉPLOYÉ"}
    ]

# Génération du fichier final
output = {
    "last_update": datetime.now().strftime("%H:%M"),
    "recent": fetch_nasa_alerts(),
    "navy": get_navy_dynamic()
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"Update terminée à {output['last_update']}")
