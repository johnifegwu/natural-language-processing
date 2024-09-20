from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re

session = HTMLSession()

def scrape_buttons_in_website(url):
    response = session.get(url)  # send a GET request to the url
    soup = BeautifulSoup(response.content, 'html.parser')  # extract the html content

    # Find all <a> tags
    links = soup.find_all('a', href=True)
    matches = []

    # Extract the href values and construct valid URLs
    for link in links:
        href = link['href'].strip()

        # Handle relative URLs
        if href.startswith('/'):
            final_url = f'{url.rstrip("/")}{href}'
        # Handle absolute URLs
        elif href.startswith('http'):
            final_url = href
        else:
            continue  # Skip other formats (like mailto, javascript links, etc.)

        matches.append(final_url)

    return matches

def scrape_email_from_website(url):
    matches = scrape_buttons_in_website(url)
    emails = set()

    # Iterate through the links and scrape emails
    for link in matches:
        try:
            response = session.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            emails.update(set(re.findall(email_pattern, soup.get_text())))
        except Exception as e:
            print(f'Error: {e}')
            continue

    return list(emails)

url = 'https://qoutes.toscrape.com'
result = scrape_email_from_website(url)
print(result)
