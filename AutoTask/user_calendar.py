
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
    return None

token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6IlM2RFlpUThnbmJCUU84MEpQY1haSFlCWnI3bndHcGhDaUR3aWdHcV9xV3ciLCJhbGciOiJSUzI1NiIsIng1dCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSIsImtpZCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lN2JhYWVlZi01NmJlLTQ4ZWItYjRmOS0zOGMwNDM0MjVjNTcvIiwiaWF0IjoxNzEzMjY3OTQyLCJuYmYiOjE3MTMyNjc5NDIsImV4cCI6MTcxMzI3MjIzNiwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFUUUF5LzhXQUFBQW1HZExMSEN2SmRlRjdyVG9xeVhITDBFVFFwYkRsVnJ4S3RUTlplY01BM1JqNTVnYytrb0s3V1RpMHEvYUhLOVUiLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6Ik1haWwgQXV0b21hdGlvbiIsImFwcGlkIjoiNzNmZDFlM2YtMTM1OS00NDJiLWJhNmYtMGM4NzU4NTFmMmJmIiwiYXBwaWRhY3IiOiIxIiwiZmFtaWx5X25hbWUiOiJSYWNoYWJhdGh1bmkiLCJnaXZlbl9uYW1lIjoiR2F5YXRocmkiLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiIxMTUuMjQ3LjEzLjEzMCIsIm5hbWUiOiJHYXlhdGhyaSBSYWNoYWJhdGh1bmkiLCJvaWQiOiJkODk0ZTViOS0zMjY1LTQ3YjgtYjBiZS03M2U3NWI1ODk2YmMiLCJwbGF0ZiI6IjMiLCJwdWlkIjoiMTAwMzIwMDM2QUI1NjE3NCIsInJoIjoiMC5BVk1BNzY2NjU3NVc2MGkwLVRqQVEwSmNWd01BQUFBQUFBQUF3QUFBQUFBQUFBQlRBQzAuIiwic2NwIjoiQ2FsZW5kYXJzLlJlYWQgQ2FsZW5kYXJzLlJlYWQuU2hhcmVkIENhbGVuZGFycy5SZWFkQmFzaWMgQ2FsZW5kYXJzLlJlYWRXcml0ZSBDYWxlbmRhcnMuUmVhZFdyaXRlLlNoYXJlZCBNYWlsLlJlYWQgTWFpbC5TZW5kIG9wZW5pZCBwcm9maWxlIFVzZXIuUmVhZCBVc2VyLlJlYWRCYXNpYy5BbGwgZW1haWwiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJuRl9uN3pEZkNBanEtR2Jqc1M3SEhSRl80UURKX19oWV9TbE1BMDRKdlA0IiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IkFTIiwidGlkIjoiZTdiYWFlZWYtNTZiZS00OGViLWI0ZjktMzhjMDQzNDI1YzU3IiwidW5pcXVlX25hbWUiOiJnYXlhdGhyaS5yYWNoYWJhdGh1bmlAd2Fsa2luZ3RyZWUudGVjaG5vbG9neSIsInVwbiI6ImdheWF0aHJpLnJhY2hhYmF0aHVuaUB3YWxraW5ndHJlZS50ZWNobm9sb2d5IiwidXRpIjoiT0dudnJOQXVIRS1RWlN6OUk4ZGNBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19zdCI6eyJzdWIiOiJyZlItRzg4ME9kbmRQUm9IQTl6dXVkcHpuVTZqaDNjOFBkemstTDZsZjBzIn0sInhtc190Y2R0IjoxNTk0MTQ1NDA1fQ.0URkGBwCc5m3l3LvoEx1yjMreZQ80ipomANWwkgKWJeqNHTljXY8RN6S__o3PB4N1Xh_fSiUq7oMZNrexKZsbnFLaWNAqkPR9OIhAehsvMMvTg_7cBCiknSVFumvIsXt8lx1QKrNSHkT9PAHFh-6xPe0OObph0ToA3T2zJn6mpsan1c0iOF3N-s1Lf9J6pM1C0TzLiv1vAawuiemWLcpD1i_DU6xI_j2YsJOrbsvxXoCdeT8ZfHG4RIByVgdYtnH5alfnZH0Va_sZTAp4DjrSk-0XjMcB_Ol6rcpf4Zz1HOXK8hZA2ajRwpFu7JDE0vh4IF3bhqrSpRkmzBZe7qzBg"
GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
MESSAGES_ENDPOINT = "/me/messages"

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
