import os
import json
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
import phonenumbers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Path to the service account key file
SERVICE_ACCOUNT_FILE = 'C:/Users/Public/goauth2/gentle-platform-436107-d7-ebcec4f3587a.json'

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
def send_campaigns(topics: Dict[str, List[Dict[str, Any]]]):
    for topic, contacts in topics.items():
        for contact in contacts:
            print(f"Sending {topic} campaign to {contact['name']} at {contact['email']}")

# Main onboarding flow
def onboarding_flow():
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
    send_campaigns(topic_contacts)

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
