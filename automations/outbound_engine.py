import requests
from bs4 import BeautifulSoup
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import time
from ratelimit import limits, sleep_and_retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from validate_email_address import validate_email
import logging
import re
import html 
from requests_html import HTMLSession

session = HTMLSession()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a regex pattern for detecting email addresses
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Constants
SENDGRID_API_KEY = 'YOUR_SENDGRID_API_KEY'
RATE_LIMIT_CALLS = 1  # Number of API calls allowed per minute
RATE_LIMIT_PERIOD = 20  # Time period in seconds for rate limit

# Dictionary of roles and associated keywords
roles_keywords = {
    'CEO': ['chief executive officer', 'ceo', 'business owner'],
    'CTO': ['chief technology officer', 'cto', 'technology head'],
    'Marketing Manager': ['marketing manager', 'digital marketing', 'social media'],
    'Sales Director': ['sales director', 'head of sales', 'sales leader'],
    'HR Manager': ['human resources manager', 'hr manager', 'talent acquisition']
}

# function to scrape all buttons with links from the website
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

# Building upon the previous step, we enhance our script to extract email addresses from the links obtained.
def scrape_email_from_website(url):
    matches = scrape_buttons_in_website(url)
    emails = set()

    # Iterate through the links and scrape emails
    for link in matches:
        try:
            response = session.get(link)
            soup = BeautifulSoup(response.content, 'lxml')
            email_pattern = re.compile(EMAIL_REGEX)
            emails.update(set(re.findall(email_pattern, soup.get_text())))
        except Exception as e:
            print(f'Error: {e}')
            continue

    return emails

# Function to use Google Custom Search API to find more CEOs
def search_via_google(query, api_key, cse_id, num=10):
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

# Step 1: Rate-limited email scraping function
@sleep_and_retry
@limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
def scrape_emails(keyword):
    """Scrape emails from a Google search page based on the keyword."""
    try:
        # Additional search using Google Custom Search API
        api_key = 'AIzaSyBLR1OzK0FcZXt1s23OcpIBMcbPfBcfl9w'
        cse_id = 'a0b0ec38d8b204551'
        google_result = search_via_google(f"{keyword}", api_key, cse_id)

        print(f"Goegle CEOs {google_result}")

        """Loop through the returned links and fetch the pages and try to extract email addresses."""
        # Initialize a set to collect emails
        all_emails = set()
        for search_link in google_result:
            # try to extract email addresses from the website
            all_emails.update(scrape_email_from_website(search_link))

        return list(all_emails)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during scraping for {keyword}: {e}")
        return []

# Step 2: Function to send email using SendGrid
def send_email(recipient_email, subject, content):
    """Send email using SendGrid."""
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = "your-email@example.com"
    
    try:
        mail = Mail(from_email=from_email, to_emails=recipient_email, subject=subject, plain_text_content=content)
        response = sg.send(mail)
        logging.info(f"Email sent to {recipient_email} with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {str(e)}")

# Step 3: Worker function for scraping and sending emails in parallel
def scrape_and_send(role, keyword):
    """Scrape emails for a role and send emails to them."""
    emails = scrape_emails(keyword)
    for email in emails:
        subject = f"Exclusive Offer for {role}s"
        content = f"Dear {role}, we have a SaaS solution tailored to your needs."
        send_email(email, subject, content)

# Step 4: Orchestrating the process with scaling
def automate_outbound_engine():
    """Automate scraping and email sending for each role using parallel processing."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for role, keywords in roles_keywords.items():
            for keyword in keywords:
                futures.append(executor.submit(scrape_and_send, role, keyword))
        
        for future in as_completed(futures):
            try:
                future.result()  # Check for any exceptions in threads
            except Exception as e:
                logging.error(f"Error in worker thread: {e}")

if __name__ == "__main__":
    start_time = time.time()
    automate_outbound_engine()
    logging.info(f"Process completed in {time.time() - start_time} seconds")
