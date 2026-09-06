import requests
import json
import sys
import time

def fetch_architects_lombardy():
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Optimized query: avoids heavy regex on keys, uses direct matches and a safer text scan.
    query = """
    [out:json][timeout:180];
    area["name"="Lombardia"]["admin_level"="4"]->.searchArea;
    (
      node["office"="architect"](area.searchArea);
      way["office"="architect"](area.searchArea);
      relation["office"="architect"](area.searchArea);

      node["office"="engineer"](area.searchArea);
      way["office"="engineer"](area.searchArea);
      relation["office"="engineer"](area.searchArea);

      node["office"]["name"~"architet|associati|studio|progetti|bim|design",i](area.searchArea);
      way["office"]["name"~"architet|associati|studio|progetti|bim|design",i](area.searchArea);
      relation["office"]["name"~"architet|associati|studio|progetti|bim|design",i](area.searchArea);
    );
    out center;
    """
    
    headers = {
        "User-Agent": "JobHuntRadarBot/1.2 (sarahalemam.37@gmail.com)"
    }
    
    print("Querying OpenStreetMap database...")
    
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
        sys.exit(1)
        
    data = response.json()
    
    # SAFETY CHECK: If the server returns a memory/timeout error inside a 200 OK response
    if 'remark' in data and not data.get('elements'):
        print(f"API Error (Remark): {data['remark']}")
        sys.exit(1)
        
    elements = data.get('elements', [])
    if len(elements) == 0:
        print("Query returned 0 results. Exiting to prevent wiping the map.")
        sys.exit(1)
        
    firms = []
    seen_coords = set()
    
    for el in elements:
        tags = el.get('tags', {})
        lat = el.get('lat') or el.get('center', {}).get('lat')
        lon = el.get('lon') or el.get('center', {}).get('lon')
        
        if not lat or not lon: continue
        
        # Prevent duplicate entries if a firm matches multiple criteria
        coord_key = f"{lat},{lon}"
        if coord_key in seen_coords: continue
        seen_coords.add(coord_key)
            
        address_parts = [f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(), tags.get('addr:city', '')]
        address = ", ".join(filter(None, address_parts))
        
        firms.append({
            "name": tags.get('name', 'Studio (Nome non specificato)'),
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
