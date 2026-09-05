import requests
import json

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
    
    print("Querying database...")
    response = requests.post(overpass_url, data={'data': query})
    if response.status_code != 200: return
    
    firms = []
    for el in response.json().get('elements', []):
        tags = el.get('tags', {})
        lat = el.get('lat') or el.get('center', {}).get('lat')
        lon = el.get('lon') or el.get('center', {}).get('lon')
        
        if not lat or not lon: continue
            
        address = ", ".join(filter(None, [f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(), tags.get('addr:city', '')]))
        
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
        
if __name__ == "__main__":
    fetch_architects_lombardy()
