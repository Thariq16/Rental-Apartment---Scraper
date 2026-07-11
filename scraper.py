import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_listings():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    base_urls = [
        'https://ikman.lk/en/ads/dehiwala/apartment-rentals',
        'https://ikman.lk/en/ads/dehiwala/house-rentals',
        'https://ikman.lk/en/ads/colombo-6/apartment-rentals',
        'https://ikman.lk/en/ads/colombo-6/house-rentals'
    ]
    
    listings = []
    
    for base_url in base_urls:
        url = f'{base_url}?enum.bedrooms=2&enum.bathrooms=2'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        for item in soup.find_all('a', class_='gtm-ad-item'):
            title_elem = item.find('h2')
            title = title_elem.text.strip() if title_elem else 'No Title'
            
            # Unfurnished Filter: Skip if "furnished" is found but not "unfurnished"
            text_lower = item.text.lower()
            if 'furnished' in text_lower and 'unfurnished' not in text_lower:
                continue
            
            price_match = re.search(r'Rs ([\d,]+)(?: /month)?', item.text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                price_val = int(price_str)
                
                # Price Filter: 75,000 to 135,000
                if 75000 <= price_val <= 135000:
                    link = item['href'] if item.has_attr('href') else '#'
                    if not link.startswith('http'):
                        link = f"https://ikman.lk{link}"
                    
                    # Format price nicely with commas for display
                    display_price = f"Rs {price_val:,}"
                    
                    listings.append({
                        'title': title,
                        'price': display_price,
                        'link': link,
                        'date_scraped': datetime.now().strftime("%Y-%m-%d")
                    })
            
    return listings

# Run and save to JSON
new_listings = scrape_listings()
with open('listings.json', 'w', encoding='utf-8') as f:
    json.dump(new_listings, f, indent=4, ensure_ascii=False)
print(f"Scraped {len(new_listings)} listings.")