import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone, timedelta
import re

def scrape_listings():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    sources = [
        {'type': 'apartment', 'url': 'https://ikman.lk/en/ads/dehiwala/apartment-rentals'},
        {'type': 'house', 'url': 'https://ikman.lk/en/ads/dehiwala/house-rentals'},
        {'type': 'apartment', 'url': 'https://ikman.lk/en/ads/colombo-6/apartment-rentals'},
        {'type': 'house', 'url': 'https://ikman.lk/en/ads/colombo-6/house-rentals'}
    ]
    
    listings = []
    seen_links = set()
    
    # Exclude upper floors for houses
    upper_floor_keywords = [
        '1st floor', 'first floor', '2nd floor', 'second floor', 
        '3rd floor', 'third floor', 'upstair', 'upstairs', 'top floor'
    ]
    
    # Strict location filter keywords
    target_locations = ['dehiwala', 'wellawatte', 'wellawatta', 'colombo 6', 'colombo-6']
    
    # Calculate Sri Lanka Time (UTC + 5:30)
    sl_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    formatted_datetime = sl_time.strftime("%Y-%m-%d %I:%M %p")

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
            link_lower = link.lower()
            
            # Filter 1: Strict Location Check (Skip promoted ads from Ja-Ela, Hantana, etc.)
            if not any(loc in text_lower or loc in link_lower for loc in target_locations):
                continue

            # Filter 2: Houses must be ground floor
            if category_type == 'house':
                if any(kw in text_lower for kw in upper_floor_keywords):
                    continue
            
            # Filter 3: Furnishing check (Exclude Fully Furnished)
            if 'fully furnished' in text_lower or 'fully-furnished' in text_lower:
                continue
            if 'furnished' in text_lower and not ('unfurnished' in text_lower or 'semi' in text_lower):
                continue

            # Filter 4: Price check (Under 135,000 LKR)
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
                        'date_scraped': formatted_datetime
                    })
            
    return listings

if __name__ == "__main__":
    new_listings = scrape_listings()
    with open('listings.json', 'w', encoding='utf-8') as f:
        json.dump(new_listings, f, indent=4, ensure_ascii=False)

    print(f"Scraped {len(new_listings)} strict local listings.")
