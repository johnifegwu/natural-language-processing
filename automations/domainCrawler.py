import requests
from bs4 import BeautifulSoup
import tweepy
import smtplib
from email.mime.text import MIMEText

# Step 1: Fetch top backlinks for a domain
def get_top_backlinks(domain):
    api_key = 'your_ahrefs_or_semrush_api_key'
    url = f'https://api.backlink_service.com/v1/backlinks?target={domain}&api_key={api_key}'
    response = requests.get(url)
    backlinks = response.json().get('backlinks', [])
    return [link['source_url'] for link in backlinks]

# Step 2: Extract author emails from the backlink sites
def extract_author_email(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Simple method to find emails from the site
    email = None
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']:
            email = a['href'].replace('mailto:', '')
            break
    return email

# Step 3: Find author on social media (using Twitter as an example)
def find_author_on_twitter(name):
    consumer_key = 'your_twitter_consumer_key'
    consumer_secret = 'your_twitter_consumer_secret'
    access_token = 'your_twitter_access_token'
    access_token_secret = 'your_twitter_access_secret'
    
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    
    # Search for user by name
    users = api.search_users(q=name)
    if users:
        user = users[0]
        return user.screen_name
    return None

# Step 4: Follow the author on Twitter
def follow_author_on_twitter(username):
    api.create_friendship(screen_name=username)

# Step 5: Send outbound email to the author
def send_email(to_email, subject, body):
    from_email = 'your_email@example.com'
    password = 'your_email_password'
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

# Main process
def main(domain):
    backlinks = get_top_backlinks(domain)
    
    for backlink in backlinks:
        print(f'Checking backlink: {backlink}')
        email = extract_author_email(backlink)
        
        if email:
            print(f'Found email: {email}')
            # Optionally find author on Twitter
            # social_media_profile = find_author_on_twitter(author_name)
            # follow_author_on_twitter(social_media_profile)
            
            # Send an outbound email to the author
            send_email(email, "Outreach", "Hi, I found your site through a backlink.")
        else:
            print(f"No email found for: {backlink}")

# Usage
if __name__ == "__main__":
    main('example.com')
