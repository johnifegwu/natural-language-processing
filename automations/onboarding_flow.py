import os
import json
import requests
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
import phonenumbers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from typing import Any, Dict

# Path to the service account key file
SERVICE_ACCOUNT_FILE = 'C:/Users/Public/goauth2/gentle-platform-436107-d7-ebcec4f3587a.json'


# Step 1: Create a campaign
def create_campaign(api_key: str, server_prefix: str, list_id: str, subject: str, from_name: str, reply_to: str):
    # Campaign creation API endpoint
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns"
    
    # Create the payload for campaign creation
    data = {
        "type": "regular",
        "recipients": {
            "list_id": list_id  # Audience ID where the email will be sent
        },
        "settings": {
            "subject_line": subject,
            "title": subject,  # Optional: title for internal reference
            "from_name": from_name,
            "reply_to": reply_to,
        }
    }
    
    # MailChimp API requires basic auth with any username and the API key as password
    auth = ("anystring", api_key)
    
    # Send POST request to create the campaign
    response = requests.post(url, json=data, auth=auth)
    
    if response.status_code == 200:
        campaign_id = response.json().get("id")
        print(f"Campaign created successfully with ID: {campaign_id}")
        return campaign_id
    else:
        print(f"Failed to create campaign. Response: {response.status_code} - {response.text}")
        return None

# Step 2: Add content to the campaign
def add_campaign_content(api_key: str, server_prefix: str, campaign_id: str, content: str):
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns/{campaign_id}/content"
    
    data = {
        "html": content  # Email body in HTML
    }
    
    auth = ("anystring", api_key)
    
    response = requests.put(url, json=data, auth=auth)
    
    if response.status_code == 200:
        print(f"Content added to campaign {campaign_id} successfully.")
    else:
        print(f"Failed to add content to campaign {campaign_id}. Response: {response.status_code} - {response.text}")

# Step 3: Send the campaign
def send_campaign(api_key: str, server_prefix: str, campaign_id: str):
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/campaigns/{campaign_id}/actions/send"
    
    auth = ("anystring", api_key)
    
    response = requests.post(url, auth=auth)
    
    if response.status_code == 204:
        print(f"Campaign {campaign_id} sent successfully!")
    else:
        print(f"Failed to send campaign {campaign_id}. Response: {response.status_code} - {response.text}")

# Function to send campaigns via MailChimp
def send_email(api_key: str, server_prefix: str, list_id: str, recipient_name: str, recipient_email: str, topic: str):
    # Define email subject and body content
    subject = f"{topic} - Special Announcement"
    from_name = "Your Company"
    reply_to = "your-email@example.com"
    
    # Campaign content (you can customize this)
    content = f"""
    <h1>Hi {recipient_name},</h1>
    <p>We have exciting news about {topic}!</p>
    <p>Stay tuned for more details.</p>
    """
    
    # Step 1: Create a new campaign
    campaign_id = create_campaign(api_key, server_prefix, list_id, subject, from_name, reply_to)
    
    if campaign_id:
        # Step 2: Add the content to the created campaign
        add_campaign_content(api_key, server_prefix, campaign_id, content)
        
        # Step 3: Send the campaign
        send_campaign(api_key, server_prefix, campaign_id)

# Function to fetch contacts from iOS (Placeholder for iOS API integration)
def fetch_ios_contacts() -> List[Dict[str, Any]]:
    # You will need to replace this part with actual API calls using provided keys.
    ios_contacts = [
        {"name": "John Doe", "email": "john@tech.com", "phone": "+14155552671"},
        {"name": "Jane Smith", "email": "jane@doctors.com", "phone": "+14155552672"},
    ]
    return ios_contacts


# Function to fetch Gmail contacts using Google API
def fetch_gmail_contacts() -> List[Dict[str, Any]]:
    # Load the service account credentials
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

    # Build the Google People API service
    service = build('people', 'v1', credentials=creds)

    # Fetch the contacts
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=1000,
        personFields='names,emailAddresses,phoneNumbers'
    ).execute()

    # Extract and format the contacts
    connections = results.get('connections', [])
    contacts = []
    for person in connections:
        name = person.get('names', [{}])[0].get('displayName', 'Unknown')
        email = person.get('emailAddresses', [{}])[0].get('value', '')
        phone = person.get('phoneNumbers', [{}])[0].get('value', '')
        contacts.append({"name": name, "email": email, "phone": phone})

    return contacts

# Function to normalize and validate phone numbers
def normalize_phone_number(phone: str) -> str:
    try:
        phone_number = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return phone

# Machine Learning-based topic assignment
def assign_topics_ml(contacts: List[Dict[str, Any]], model, vectorizer) -> Dict[str, List[Dict[str, Any]]]:
    topics = {"Technology": [], "Health": [], "Education": []}
    
    # Extract features (name and email) to assign topics
    contact_features = [f"{contact['name']} {contact['email']}" for contact in contacts]
    
    # Vectorize contact features
    X = vectorizer.transform(contact_features)
    
    # Predict topics using the ML model
    predicted_topics = model.predict(X)

    # Map predictions to the corresponding contacts
    for idx, topic in enumerate(predicted_topics):
        topics[topic].append(contacts[idx])

    return topics

# Function to send campaigns to topic-specific contacts
def send_campaigns(api_key: str, server_prefix: str, list_id: str, topics: Dict[str, Any]):
    for topic, contacts in topics.items():
        for contact in contacts:
            recipient_name = contact['name']
            recipient_email = contact['email']
            
            # Log or print the action of sending
            print(f"Sending {topic} campaign to {recipient_name} at {recipient_email}")
            
            # Send email using the email sending function
            send_email(api_key, server_prefix, list_id, recipient_name, recipient_email, topic)

# Main onboarding flow
def onboarding_flow():
    api_key = "your_mailchimp_api_key"
    server_prefix = "usX"  # The 'X' is replaced by the prefix found in your API key, e.g., "us1", "us2"
    list_id = "your_list_id"  # Your MailChimp Audience ID

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

    # Step 5: Send campaigns to contacts based on their assigned topics
    send_campaigns(api_key, server_prefix, list_id, topic_contacts)

# Training the ML Model (Naive Bayes)
def train_ml_model():
    # Example training data (name/email to topic mapping)
    training_data = [
        {"name": "John Doe", "email": "john@techcorp.com", "topic": "Technology"},
        {"name": "Dr. Jane Smith", "email": "jane@healthclinic.com", "topic": "Health"},
        {"name": "Emily Doe", "email": "emily@university.edu", "topic": "Education"},
    ]
    
    # Preparing training features and labels
    training_features = [f"{data['name']} {data['email']}" for data in training_data]
    training_labels = [data["topic"] for data in training_data]
    
    # Vectorize the text features (name + email)
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(training_features)
    
    # Train a Naive Bayes classifier
    model = MultinomialNB()
    model.fit(X_train, training_labels)
    
    return model, vectorizer

# Run the onboarding flow
if __name__ == "__main__":
    onboarding_flow()
