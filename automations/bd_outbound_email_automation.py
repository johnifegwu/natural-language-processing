import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from googleapiclient.discovery import build
from linkedin_api import Linkedin

# Extract LinkedIn network and Google contacts
def fetch_google_contacts(api_key, target_industry, target_roles):
    # Use Google People API to fetch contacts
    service = build('people', 'v1', developerKey=api_key)
    contacts = service.people().connections().list(resourceName='people/me', personFields='names,emailAddresses,occupations').execute()
    
    relevant_contacts = []
    for contact in contacts.get('connections', []):
        name = contact.get('names', [{}])[0].get('displayName', '')
        email = contact.get('emailAddresses', [{}])[0].get('value', '')
        occupation = contact.get('occupations', [{}])[0].get('value', '')
        
        if any(role in occupation for role in target_roles) and target_industry in occupation:
            relevant_contacts.append({
                'name': name,
                'email': email,
                'occupation': occupation
            })
    return relevant_contacts

def fetch_linkedin_contacts(linkedin_username, linkedin_password, target_industry, target_roles):
    api = Linkedin(linkedin_username, linkedin_password)
    connections = api.get_profile_connections()

    relevant_contacts = []
    for connection in connections:
        occupation = connection['headline']
        if any(role in occupation for role in target_roles) and target_industry in occupation:
            relevant_contacts.append({
                'name': connection['firstName'] + " " + connection['lastName'],
                'email': connection.get('email', ''),  # You can enrich this using other tools like Clearbit
                'occupation': occupation,
                'engagement_strength': connection['mutualConnections']  # Or other metrics like message frequency
            })
    return relevant_contacts

# Combine contacts and rank by engagement strength
def rank_contacts_by_engagement(contacts):
    # Sort based on engagement strength or any other criteria
    return sorted(contacts, key=lambda x: x.get('engagement_strength', 0), reverse=True)


# Automate outbound email sequence using SendGrid
def send_email_with_sendgrid(contact, email_body, subject, sender_email, sendgrid_api_key):
    # Prepare email content
    message = Mail(
        from_email=sender_email,
        to_emails=contact['email'],
        subject=subject.format(industry=contact.get('occupation', '')),
        plain_text_content=email_body.format(name=contact['name'], industry=contact.get('occupation', ''))
    )
    
    try:
        # Send the email using SendGrid
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent to {contact['name']} with status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {contact['name']}: {e}")

def run_outbound_email_sequence_with_sendgrid(contacts, email_body, subject, sender_email, sendgrid_api_key):
    for contact in contacts:
        send_email_with_sendgrid(contact, email_body, subject, sender_email, sendgrid_api_key)

# usage
def main():
    google_api_key = 'AIzaSyBLR1OzK0FcZXt1s23OcpIBMcbPfBcfl9w'
    linkedin_username = 'your_linkedin_username'
    linkedin_password = 'your_linkedin_password'
    target_industry = 'Enterprise Software'
    target_roles = ['CTO', 'VP of Engineering', 'Tech Lead']

    # Fetch contacts from Google and LinkedIn
    google_contacts = fetch_google_contacts(google_api_key, target_industry, target_roles)
    linkedin_contacts = fetch_linkedin_contacts(linkedin_username, linkedin_password, target_industry, target_roles)

    # Combine and rank contacts
    all_contacts = google_contacts + linkedin_contacts
    ranked_contacts = rank_contacts_by_engagement(all_contacts)

    # Email setup using SendGrid
    sendgrid_api_key = 'your_sendgrid_api_key'  # Add your SendGrid API key here
    sender_email = 'your_email@domain.com'
    email_body = "Hi {name},\n\nI wanted to reach out regarding an exciting opportunity in the {industry}."
    subject = "Exciting Opportunity in {industry}"

    # Send outbound email sequence with SendGrid
    run_outbound_email_sequence_with_sendgrid(ranked_contacts, email_body, subject, sender_email, sendgrid_api_key)

if __name__ == "__main__":
    main()
