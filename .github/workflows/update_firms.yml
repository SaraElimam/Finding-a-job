import requests
import json
import sys

def fetch_architects_lombardy():
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    query = """
    [out:json][timeout:60];
    area["name"="Lombardia"]["admin_level"="4"]->.searchArea;
    (
      node["office"="architect"](area.searchArea);
      way["office"="architect"](area.searchArea);
      relation["office"="architect"](area.searchArea);
    );
    out center;
    """
    
    # OpenStreetMap requires a custom User-Agent to accept the request
    headers = {
        "User-Agent": "JobHuntRadarBot/1.0 (sarahalemam.37@gmail.com)"
    }
    
    print("Querying OpenStreetMap database...")
    response = requests.post(overpass_url, data={'data': query}, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching data: HTTP {response.status_code}")
        print(response.text)
        sys.exit(1) # This forces the GitHub Action to fail properly if the API rejects the request
    
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
            "address": address or "Indirizzo non disponibile",
            "website": tags.get('website', tags.get('contact:website', '')),
            "phone": tags.get('phone', tags.get('contact:phone', 'N/A'))
        })
        
    with open('firms.json', 'w', encoding='utf-8') as f:
        json.dump(firms, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {len(firms)} firms to firms.json.")

if __name__ == "__main__":
    fetch_architects_lombardy()
