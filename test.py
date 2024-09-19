from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re

session = HTMLSession()

def scrape_buttons_in_website(url):
    response = session.get(url) # send a GET request to the url
    soup = BeautifulSoup(response.content, 'html.parser') # extract the html content

    data = str(soup.find_all('a')) # find all <a> tags
    matches = []

    # Extract links from the HTML content
    for match in re.finditer('href="/', data):
        find = data[match.start() + 6:match.end() + 30]
        find = find[:find.find('"')].strip()
        
        # Construct the final URL
        if find != "/":
            final_url = f'{url}{find}'
            matches.append(final_url)

    return matches

def scrape_email_from_website(url):
    matches = scrape_buttons_in_website(url)
    emails = set()

    # Iterate through the links and scrape emails
    for link in matches:
        try:
            response = session.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            emails.update(set(re.findall(email_pattern, soup.get_text())))
        except Exception as e:
            print(f'Error: {e}')
            continue

    return list(emails)


url = 'https://articture.com/en-gb'
result = scrape_email_from_website(url)
print(result)