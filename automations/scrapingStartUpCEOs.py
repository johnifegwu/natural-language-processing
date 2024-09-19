import requests
from bs4 import BeautifulSoup
import time
import json

# Function to scrape top startup CEOs from a predefined blog or website
def scrape_ceos_from_site(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to scrape {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    ceo_list = []

    # This part depends on the structure of the website you're scraping
    # Assuming the website lists names of CEOs in <h2> tags:
    for item in soup.find_all('h2'): 
        ceo_name = item.get_text(strip=True)
        ceo_list.append(ceo_name)
    
    return ceo_list

# Function to use Google Custom Search API to find more CEOs
def search_ceos_via_google(query, api_key, cse_id, num=10):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&num={num}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching from Google Custom Search API")
        return []

    search_results = response.json()
    ceo_links = []

    for item in search_results.get('items', []):
        ceo_links.append(item['link'])
    
    return ceo_links

# Function to scrape social media profiles (e.g., LinkedIn, Twitter) from websites
def scrape_social_media_profiles(ceo_page_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(ceo_page_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to scrape social profiles from {ceo_page_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    profiles = {}

    # Find LinkedIn profile
    linkedin = soup.find('a', href=lambda href: href and 'linkedin.com' in href)
    if linkedin:
        profiles['LinkedIn'] = linkedin['href']

    # Find Twitter profile
    twitter = soup.find('a', href=lambda href: href and 'twitter.com' in href)
    if twitter:
        profiles['Twitter'] = twitter['href']

    return profiles

# Main function to get the biggest possible list of startup CEOs
def get_ceo_list():
    # Predefined list of websites to scrape
    ceo_sites = [
        'https://blog.feedspot.com/startup_ceos/',
        'https://www.forbes.com/sites/forbesbusinesscouncil/2021/05/12/top-ceos-to-follow-on-twitter/',
        'https://www.businessinsider.com/top-tech-ceos-2021',
    ]
    
    all_ceos = []

    # Scrape from predefined sites
    for site in ceo_sites:
        ceos_from_site = scrape_ceos_from_site(site)
        all_ceos.extend(ceos_from_site)
        time.sleep(2)  # Be kind to servers and avoid rate limiting

    # Additional search using Google Custom Search API
    api_key = 'AIzaSyBLR1OzK0FcZXt1s23OcpIBMcbPfBcfl9w'
    cse_id = 'a0b0ec38d8b204551'
    google_ceos = search_ceos_via_google("top startup CEOs to follow", api_key, cse_id)
        
    # Print Google List
    print(f"Here is a from google:\n {google_ceos}")

    for ceo_link in google_ceos:
        profiles = scrape_social_media_profiles(ceo_link)
        if profiles:
            all_ceos.append(profiles)
    
    return all_ceos

if __name__ == "__main__":
    ceo_list = get_ceo_list()
    
    # Print or save the result
    print("Here is the list of startup CEOs:\n")
    print(json.dumps(ceo_list, indent=2))
