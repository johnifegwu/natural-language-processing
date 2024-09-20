from selenium import webdriver
from bs4 import BeautifulSoup
import re

# Define a regex pattern for detecting email addresses
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def scrape_buttons_in_website(url):
    # Set up Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome WebDriver
    service = webdriver.ChromeService()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Fetch the website
        driver.get(url)
        # Extract the page source and pass to BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        # Close the browser
        driver.quit()

    # Debugging: Check if you're getting proper content
    print(soup.prettify())  # Print the HTML content

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
    # Set up Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome WebDriver
    service = webdriver.ChromeService()

    # Iterate through the links and scrape emails
    for link in matches:
        try:
            driver = webdriver.Chrome(service=service, options=options)
            # Fetch the website
            driver.get(link)

            # Extract the page source and pass to BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            email_pattern = re.compile(EMAIL_REGEX)
            emails.update(set(re.findall(email_pattern, soup.get_text())))
        except Exception as e:
            print(f'Error scraping {link}: {e}')
        finally:
            driver.quit()
            # Debugging: Check if you're getting proper content
            print(soup.prettify())  # Print the HTML content

    return list(emails)

url = 'https://articture.com/en-gb'
result = scrape_email_from_website(url)
print(result)
