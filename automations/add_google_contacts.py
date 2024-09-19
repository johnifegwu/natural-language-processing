from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the service account key file directly
SERVICE_ACCOUNT_FILE = 'C:/Users/Public/goauth2/gentle-platform-436107-d7-ebcec4f3587a.json'

def add_google_contacts(contacts: list):
    # Use service account credentials
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

    # Build the service
    service = build('people', 'v1', credentials=creds)

    # Loop through each contact and create them
    for contact in contacts:
        new_contact = {
            "names": [
                {
                    "givenName": contact.get("givenName"),
                    "familyName": contact.get("familyName")
                }
            ],
            "emailAddresses": [
                {
                    "value": contact.get("email")
                }
            ],
            "phoneNumbers": [
                {
                    "value": contact.get("phone")
                }
            ]
        }
        service.people().createContact(body=new_contact).execute()
        print(f"Contact {contact.get('givenName')} {contact.get('familyName')} added successfully!")


# Example list of contacts to add
contacts_list = [
    {
        "givenName": "John",
        "familyName": "Doe",
        "email": "johndoe@example.healt",
        "phone": "+14155552671"
    },
    {
        "givenName": "Jane",
        "familyName": "Smith",
        "email": "janesmith@example.tech",
        "phone": "+14155552672"
    },
    {
        "givenName": "Emily",
        "familyName": "Clark",
        "email": "emily.clark@example.edu",
        "phone": "+14155552673"
    }
]

# Call the function to add multiple contacts
if __name__ == "__main__":
    add_google_contacts(contacts_list)
