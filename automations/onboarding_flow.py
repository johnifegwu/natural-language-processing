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
    from_name = "Your Company"
    reply_to = "your-email@example.com"
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
    server_prefix = "usX"
    list_id = "your_list_id"

    ios_contacts = fetch_ios_contacts()
    gmail_contacts = fetch_gmail_contacts()
    all_contacts = ios_contacts + gmail_contacts

    for contact in all_contacts:
        contact['phone'] = normalize_phone_number(contact.get('phone', ''))

    try:
        model, vectorizer = train_ml_model()
        topic_contacts = assign_topics_ml(all_contacts, model, vectorizer)
        send_campaigns(api_key, server_prefix, list_id, topic_contacts)
    except Exception as e:
        print(f"Failed during onboarding flow: {str(e)}")

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
