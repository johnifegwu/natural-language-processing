import os
import json
import requests
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
import phonenumbers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Path to the service account key file
SERVICE_ACCOUNT_FILE = 'C:/Users/Public/goauth2/gentle-platform-436107-d7-ebcec4f3587a.json'
COMPANY_NAME = "My Company Name"
COMPANY_EMAIL = "your-email@example.com"

# Creates a list with contacts
def create_list_with_contacts(api_key: str, server_prefix: str, topic: str, contacts: List[Dict[str, Any]]) -> str:
    """Create a new MailChimp list (audience) for a given topic and add contacts."""
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/lists"
    auth = ("anystring", api_key)
    
    # List creation payload
    data = {
        "name": topic,
        "contact": {
            "company": COMPANY_NAME,
            "address1": "123 Main St",
            "city": "Anytown",
            "state": "State",
            "zip": "12345",
            "country": "US",
            "phone": "123-456-7890"
        },
        "permission_reminder": "You signed up for updates on our website",
        "campaign_defaults": {
            "from_name": COMPANY_NAME,
            "from_email": COMPANY_EMAIL,
            "subject": f"Updates on {topic}",
            "language": "EN_US"
        },
        "email_type_option": True
    }
    
    response = requests.post(url, json=data, auth=auth)
    
    if response.status_code == 200:
        list_id = response.json().get("id")
        print(f"List for topic '{topic}' created successfully with ID: {list_id}")
        
        # After the list is created, add the contacts
        for contact in contacts:
            add_contact_to_list(api_key, server_prefix, list_id, contact)
        
        return list_id
    else:
        print(f"Failed to create list for topic '{topic}'. Response: {response.status_code} - {response.text}")
        return None

# Function to add missing contacts
def add_missing_contacts_to_list(api_key: str, server_prefix: str, list_id: str, new_contacts: List[Dict[str, Any]]):
    """Add contacts to the list only if they don't already exist."""
    existing_emails = get_existing_emails(api_key, server_prefix, list_id)
    
    # Filter out the contacts that are not already in the list
    contacts_to_add = [contact for contact in new_contacts if contact['email'] not in existing_emails]
    
    if contacts_to_add:
        print(f"Adding {len(contacts_to_add)} new contact(s) to the list.")
        for contact in contacts_to_add:
            add_contact_to_list(api_key, server_prefix, list_id, contact)
    else:
        print("All contacts already exist in the list.")

# Function to get existing emails
def get_existing_emails(api_key: str, server_prefix: str, list_id: str) -> List[str]:
    """Retrieve all existing emails from the MailChimp list."""
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/lists/{list_id}/members"
    
    auth = ("anystring", api_key)
    
    # MailChimp paginates results, so we may need to retrieve multiple pages
    existing_emails = []
    offset = 0
    count = 100  # Adjust the count based on your needs
    
    while True:
        params = {"offset": offset, "count": count}
        response = requests.get(url, auth=auth, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching list members: {response.status_code} - {response.text}")
            break
        
        members = response.json().get("members", [])
        existing_emails.extend([member['email_address'] for member in members])
        
        # If there are fewer members than count, we've reached the last page
        if len(members) < count:
            break
        
        offset += count
    
    return existing_emails

# Function to Add contact to the list
def add_contact_to_list(api_key: str, server_prefix: str, list_id: str, contact: Dict[str, Any]):
    """Add a single contact to the MailChimp list."""
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/lists/{list_id}/members"
    
    data = {
        "email_address": contact['email'],
        "status": "subscribed",  # You can also use 'pending' or 'unsubscribed' based on your needs
        "merge_fields": {
            "FNAME": contact["name"],
            "PHONE": contact.get("phone", "")
        },
    }
    
    auth = ("anystring", api_key)
    
    response = requests.post(url, json=data, auth=auth)
    
    if response.status_code == 200:
        print(f"Added contact {contact['email']} to the list.")
    else:
        print(f"Failed to add contact {contact['email']}. Response: {response.status_code} - {response.text}")


# Function to create and send campaign
def create_and_send_campaign(api_key: str, server_prefix: str, topic: str, list_id: str):
    """Create and send a campaign to a specific list (by topic)."""
    subject = f"{topic} - Special Announcement"
    from_name = COMPANY_NAME
    reply_to = COMPANY_EMAIL
    
    # Create a campaign for the list
    campaign_id = create_campaign(api_key, server_prefix, list_id, subject, from_name, reply_to)
    
    if campaign_id:
        # Generate the campaign content dynamically
        content = f"""
        <h1>Hi,</h1>
        <p>We have exciting news about {topic}!</p>
        <p>Stay tuned for more details.</p>
        """
        add_campaign_content(api_key, server_prefix, campaign_id, content)
        
        # Send the campaign
        send_campaign(api_key, server_prefix, campaign_id)

# function to get list_id
def get_list_id(api_key: str, server_prefix: str, topic: str) -> str:
    """Check if a list for the topic already exists and return its list_id."""
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/lists"
    auth = ("anystring", api_key)
    
    response = requests.get(url, auth=auth)
    
    if response.status_code == 200:
        lists = response.json().get("lists", [])
        for lst in lists:
            if lst.get("name") == topic:
                return lst.get("id")  # Return the existing list_id if found
    else:
        print(f"Error fetching lists: {response.status_code} - {response.text}")
    
    return None

# Function to get campaign_id
def get_campaign_id(api_key: str, server_prefix: str, topic: str, list_id: str) -> str:
    """Check if a campaign for the topic already exists and return its campaign_id."""
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns"
    auth = ("anystring", api_key)
    
    response = requests.get(url, auth=auth)
    
    if response.status_code == 200:
        campaigns = response.json().get("campaigns", [])
        for campaign in campaigns:
            if campaign.get("settings", {}).get("title") == topic and campaign.get("recipients", {}).get("list_id") == list_id:
                return campaign.get("id")  # Return the existing campaign_id if found
    else:
        print(f"Error fetching campaigns: {response.status_code} - {response.text}")
    
    return None


# Function to send topic campaigns
def send_topic_campaigns(api_key: str, server_prefix: str, topic_contacts: Dict[str, List[Dict[str, Any]]]):
    """Send campaigns for each topic by creating a list and adding only missing contacts."""
    for topic, contacts in topic_contacts.items():
        # Check if the list already exists
        list_id = get_list_id(api_key, server_prefix, topic)
        
        if list_id:
            print(f"List for topic '{topic}' already exists with ID: {list_id}.")
            # Add only missing contacts to the list
            add_missing_contacts_to_list(api_key, server_prefix, list_id, contacts)
        else:
            # Create a new list and add all contacts
            list_id = create_list_with_contacts(api_key, server_prefix, topic, contacts)
            if not list_id:
                print(f"Error: Could not create list for topic '{topic}'. Skipping.")
                continue
        
        # Check if the campaign already exists for this topic and list
        campaign_id = get_campaign_id(api_key, server_prefix, topic, list_id)
        
        if campaign_id:
            print(f"Campaign for topic '{topic}' already exists with ID: {campaign_id}. Sending campaign...")
            # Send the existing campaign
            send_campaign(api_key, server_prefix, campaign_id)
        else:
            # Create and send a new campaign to the list
            create_and_send_campaign(api_key, server_prefix, topic, list_id)


# Step 1: Create a campaign
def create_campaign(api_key: str, server_prefix: str, list_id: str, subject: str, from_name: str, reply_to: str):
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns"
    data = {
        "type": "regular",
        "recipients": {
            "list_id": list_id
        },
        "settings": {
            "subject_line": subject,
            "title": subject,
            "from_name": from_name,
            "reply_to": reply_to,
        }
    }
    auth = ("anystring", api_key)

    try:
        response = requests.post(url, json=data, auth=auth)
        response.raise_for_status()  # Check for HTTP request errors
        campaign_id = response.json().get("id")
        if not campaign_id:
            print("Error: No campaign ID returned.")
            return None
        print(f"Campaign created successfully with ID: {campaign_id}")
        return campaign_id
    except requests.exceptions.RequestException as e:
        print(f"Failed to create campaign: {str(e)}")
        return None

# Step 2: Add content to the campaign
def add_campaign_content(api_key: str, server_prefix: str, campaign_id: str, content: str):
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns/{campaign_id}/content"
    data = {
        "html": content
    }
    auth = ("anystring", api_key)

    try:
        response = requests.put(url, json=data, auth=auth)
        response.raise_for_status()  # Check for HTTP request errors
        print(f"Content added to campaign {campaign_id} successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to add content to campaign {campaign_id}: {str(e)}")


# Step 3: Send the campaign
def send_campaign(api_key: str, server_prefix: str, campaign_id: str):
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns/{campaign_id}/actions/send"
    auth = ("anystring", api_key)

    try:
        response = requests.post(url, auth=auth)
        response.raise_for_status()  # Check for HTTP request errors
        print(f"Campaign {campaign_id} sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send campaign {campaign_id}: {str(e)}")

# Function to send campaigns via MailChimp
def send_email(api_key: str, server_prefix: str, list_id: str, recipient_name: str, recipient_email: str, topic: str):
    subject = f"{topic} - Special Announcement"
    from_name = COMPANY_NAME
    reply_to = COMPANY_EMAIL
    content = f"""
    <h1>Hi {recipient_name},</h1>
    <p>We have exciting news about {topic}!</p>
    <p>Stay tuned for more details.</p>
    """

    campaign_id = create_campaign(api_key, server_prefix, list_id, subject, from_name, reply_to)
    if campaign_id:
        add_campaign_content(api_key, server_prefix, campaign_id, content)
        send_campaign(api_key, server_prefix, campaign_id)

# Function to fetch contacts from iOS (Placeholder for iOS API integration)
def fetch_ios_contacts() -> List[Dict[str, Any]]:
    ios_contacts = [
        {"name": "John Doe", "email": "john@tech.com", "phone": "+14155552671"},
        {"name": "Jane Smith", "email": "jane@doctors.com", "phone": "+14155552672"},
    ]
    return ios_contacts

# Function to fetch Gmail contacts using Google API
def fetch_gmail_contacts() -> List[Dict[str, Any]]:
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        service = build('people', 'v1', credentials=creds)
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,
            personFields='names,emailAddresses,phoneNumbers'
        ).execute()
        connections = results.get('connections', [])
        contacts = []
        for person in connections:
            name = person.get('names', [{}])[0].get('displayName', 'Unknown')
            email = person.get('emailAddresses', [{}])[0].get('value', '')
            phone = person.get('phoneNumbers', [{}])[0].get('value', '')
            contacts.append({"name": name, "email": email, "phone": phone})
        return contacts
    except Exception as e:
        print(f"Failed to fetch Gmail contacts: {str(e)}")
        return []

# Function to normalize and validate phone numbers
def normalize_phone_number(phone: str) -> str:
    try:
        phone_number = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        print(f"Invalid phone number format: {phone}")
        return phone

# Machine Learning-based topic assignment
def assign_topics_ml(contacts: List[Dict[str, Any]], model, vectorizer) -> Dict[str, List[Dict[str, Any]]]:
    topics = {"Technology": [], "Health": [], "Education": []}
    contact_features = [f"{contact['name']} {contact['email']}" for contact in contacts]

    try:
        X = vectorizer.transform(contact_features)
        predicted_topics = model.predict(X)

        for idx, topic in enumerate(predicted_topics):
            topics[topic].append(contacts[idx])

        return topics
    except Exception as e:
        print(f"Error in topic assignment: {str(e)}")
        return topics

# Function to send campaigns to topic-specific contacts
def send_campaigns(api_key: str, server_prefix: str, list_id: str, topics: Dict[str, Any]):
    for topic, contacts in topics.items():
        for contact in contacts:
            recipient_name = contact['name']
            recipient_email = contact['email']
            try:
                print(f"Sending {topic} campaign to {recipient_name} at {recipient_email}")
                send_email(api_key, server_prefix, list_id, recipient_name, recipient_email, topic)
            except Exception as e:
                print(f"Failed to send email to {recipient_name}: {str(e)}")

# Main onboarding flow
def onboarding_flow():
    api_key = "your_mailchimp_api_key"
    server_prefix = "usX"  # Replace with your server prefix
    
    # Step 1: Fetch contacts from iOS and Gmail
    ios_contacts = fetch_ios_contacts()
    gmail_contacts = fetch_gmail_contacts()
    
    # Combine contacts from both sources
    all_contacts = ios_contacts + gmail_contacts
    
    # Step 2: Normalize and validate phone numbers
    for contact in all_contacts:
        contact['phone'] = normalize_phone_number(contact.get('phone', ''))
    
    # Step 3: Load pre-trained ML model and vectorizer
    model, vectorizer = train_ml_model()
    
    # Step 4: Assign contacts to topics using ML
    topic_contacts = assign_topics_ml(all_contacts, model, vectorizer)
    
    # Step 5: Send campaigns for each topic by creating lists with contacts
    send_topic_campaigns(api_key, server_prefix, topic_contacts)

# Training the ML Model (Naive Bayes)
def train_ml_model():
    training_data = [
        {"name": "John Doe", "email": "john@techcorp.com", "topic": "Technology"},
        {"name": "Dr. Jane Smith", "email": "jane@healthclinic.com", "topic": "Health"},
        {"name": "Emily Doe", "email": "emily@university.edu", "topic": "Education"},
    ]
    training_features = [f"{data['name']} {data['email']}" for data in training_data]
    training_labels = [data["topic"] for data in training_data]

    try:
        vectorizer = TfidfVectorizer()
        X_train = vectorizer.fit_transform(training_features)
        model = MultinomialNB()
        model.fit(X_train, training_labels)
        return model, vectorizer
    except Exception as e:
        print(f"Failed to train ML model: {str(e)}")
        return None, None

# Run the onboarding flow
if __name__ == "__main__":
    onboarding_flow()
