import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_listings():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Categorized sources to apply separate floor rules
    sources = [
        {'type': 'apartment', 'url': 'https://ikman.lk/en/ads/dehiwala/apartment-rentals'},
        {'type': 'house', 'url': 'https://ikman.lk/en/ads/dehiwala/house-rentals'},
        {'type': 'apartment', 'url': 'https://ikman.lk/en/ads/colombo-6/apartment-rentals'},
        {'type': 'house', 'url': 'https://ikman.lk/en/ads/colombo-6/house-rentals'}
    ]
    
    listings = []
    seen_links = set()
    
    # Exclude upper floor keywords for houses
    upper_floor_keywords = [
        '1st floor', 'first floor', '2nd floor', 'second floor', 
        '3rd floor', 'third floor', 'upstair', 'upstairs', 'top floor'
    ]
    
    for source in sources:
        category_type = source['type']
        base_url = source['url']
        url = f'{base_url}?enum.bedrooms=2&enum.bathrooms=2'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        for item in soup.find_all('a', class_='gtm-ad-item'):
            link = item['href'] if item.has_attr('href') else '#'
            if not link.startswith('http'):
                link = f"https://ikman.lk{link}"
            
            if link in seen_links:
                continue

            title_elem = item.find('h2')
            title = title_elem.text.strip() if title_elem else 'No Title'
            text_lower = item.text.lower()
            
            # Rule 1: Houses must be ground floor (exclude upper floor keywords)
            if category_type == 'house':
                if any(kw in text_lower for kw in upper_floor_keywords):
                    continue
            
            # Rule 2: Allow Unfurnished & Semi-Furnished; exclude Fully Furnished
            if 'fully furnished' in text_lower or 'fully-furnished' in text_lower:
                continue
            if 'furnished' in text_lower and not ('unfurnished' in text_lower or 'semi' in text_lower):
                continue

            # Rule 3: Price filter (Under 135,000 LKR)
            price_match = re.search(r'Rs ([\d,]+)(?: /month)?', item.text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                price_val = int(price_str)
                
                if price_val <= 135000:
                    display_price = f"Rs {price_val:,}"
                    
                    seen_links.add(link)
                    listings.append({
                        'title': title,
                        'price': display_price,
                        'link': link,
                        'date_scraped': datetime.now().strftime("%Y-%m-%d")
                    })
            
    return listings

if __name__ == "__main__":
    new_listings = scrape_listings()
    with open('listings.json', 'w', encoding='utf-8') as f:
        json.dump(new_listings, f, indent=4, ensure_ascii=False)

    print(f"Scraped {len(new_listings)} matching listings.")
