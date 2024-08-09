
import requests

class EmailReader:
    def __init__(self, token, GRAPH_API_BASE_URL, MESSAGES_ENDPOINT):
        self.token = token
        self.GRAPH_API_BASE_URL = GRAPH_API_BASE_URL
        self.MESSAGES_ENDPOINT = MESSAGES_ENDPOINT

    def read_sender_emails(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.MESSAGES_ENDPOINT + "?$filter=isRead eq false", headers=headers)
        if response.status_code == 200:
            emails_data = response.json().get('value', [])
            sender_emails = []
            for email_data in emails_data:
                sender_email = email_data.get('sender', {}).get('emailAddress', {}).get('address', '')
                if sender_email:
                    sender_emails.append(sender_email)
            return sender_emails
        else:
            print("Failed to fetch sender emails:", response.text)
            return []

def get_user_id_from_email(email, headers):
    # Search for users whose mail attribute matches the email address
    endpoint = f"{GRAPH_API_BASE_URL}/users?$search=\"{email}\""
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        users = response.json().get('value', [])
        if users:
            return users[0]['id']  # Return first user ID
    else:
        print(f"Failed to fetch user ID for email {email}: {response.text}")
    return 

# Initialize EmailReader
email_reader = EmailReader(token, GRAPH_API_BASE_URL, MESSAGES_ENDPOINT)

# Get sender emails from unread messages
sender_emails = email_reader.read_sender_emails()

if sender_emails:
    for sender_email in sender_emails:
        # Retrieve user ID from sender email
        user_id = get_user_id_from_email(sender_email, headers={'Authorization': 'Bearer ' + token})
        if user_id:
            print(f"User with email {sender_email} has user ID: {user_id}")
        else:
            print(f"No user found for email {sender_email}")
else:
    print("No sender emails found.")
