import requests
import json
import sys
import time

def fetch_architects_lombardy():
    # Enforce HTTPS to prevent the server from dropping the POST data during a redirect
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    query = """
    [out:json][timeout:90];
    area["name"="Lombardia"]["admin_level"="4"]->.searchArea;
    (
      // 1. Get all explicitly tagged architects and engineers
      node["office"~"^(architect|engineer)$"](area.searchArea);
      way["office"~"^(architect|engineer)$"](area.searchArea);
      relation["office"~"^(architect|engineer)$"](area.searchArea);
      
      // 2. Get generic offices if their name sounds like an AEC firm (case-insensitive)
      node["office"~"^(company|yes)$"]["name"~"arch|studio|associati|progetti|design|bim|ingegneria",i](area.searchArea);
      way["office"~"^(company|yes)$"]["name"~"arch|studio|associati|progetti|design|bim|ingegneria",i](area.searchArea);
      relation["office"~"^(company|yes)$"]["name"~"arch|studio|associati|progetti|design|bim|ingegneria",i](area.searchArea);
    );
    out center;
    """
    
    headers = {
        "User-Agent": "JobHuntRadarBot/1.1 (sarahalemam.37@gmail.com)"
    }
    
    print("Querying OpenStreetMap database...")
    
    # Implement a retry mechanism in case the free server is temporarily overloaded
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(overpass_url, data={'data': query}, headers=headers)
        
        if response.status_code == 200:
            break
            
        print(f"Attempt {attempt + 1} failed: HTTP {response.status_code}")
        if attempt < max_retries - 1:
            print("Waiting 15 seconds before retrying...")
            time.sleep(15)
    else:
        print("All attempts failed. Exiting.")
        print(response.text)
        sys.exit(1)
        
    data = response.json()
    firms = []
    
    for el in data.get('elements', []):
        tags = el.get('tags', {})
        lat = el.get('lat') or el.get('center', {}).get('lat')
        lon = el.get('lon') or el.get('center', {}).get('lon')
        
        if not lat or not lon: continue
            
        address_parts = [f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(), tags.get('addr:city', '')]
        address = ", ".join(filter(None, address_parts))
        
        firms.append({
            "name": tags.get('name', 'Studio di Architettura'),
            "lat": lat,
            "lon": lon,
            "address": address if address else "Indirizzo non disponibile",
            "website": tags.get('website', tags.get('contact:website', '')),
            "phone": tags.get('phone', tags.get('contact:phone', 'N/A'))
        })
        
    with open('firms.json', 'w', encoding='utf-8') as f:
        json.dump(firms, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {len(firms)} firms to firms.json.")

if __name__ == "__main__":
    fetch_architects_lombardy()
