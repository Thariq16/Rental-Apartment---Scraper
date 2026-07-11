import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_listings():
    # Example URL (replace with actual search URL)
    url = 'https://example-property-site.com/rent/dehiwala?beds=2&baths=2&max_price=100000'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    listings = []
    # Replace 'listing-card' with the actual HTML class used by the site
    for item in soup.find_all('div', class_='listing-card'):
        title = item.find('h2', class_='title').text.strip() if item.find('h2', class_='title') else 'No Title'
        price = item.find('span', class_='price').text.strip() if item.find('span', class_='price') else 'Price not listed'
        link = item.find('a')['href'] if item.find('a') else '#'
        
        listings.append({
            'title': title,
            'price': price,
            'link': f"https://example-property-site.com{link}",
            'date_scraped': datetime.now().strftime("%Y-%m-%d")
        })
        
    return listings

# Run and save to JSON
new_listings = scrape_listings()
with open('listings.json', 'w') as f:
    json.dump(new_listings, f, indent=4)
print(f"Scraped {len(new_listings)} listings.")