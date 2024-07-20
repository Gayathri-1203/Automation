"""
Outlook_mail:
-> Read all unread mails based on the given keyword we provided
-> reply to the mails
-> Retrives all mails related to the specific mail using same conversationID

"""
import requests
import re
import json

class EmailReader:
    def __init__(self, token, GRAPH_API_BASE_URL, MESSAGES_ENDPOINT,SENT_MESSAGES_ENDPOINT):
        self.token = token
        self.GRAPH_API_BASE_URL = GRAPH_API_BASE_URL
        self.MESSAGES_ENDPOINT = MESSAGES_ENDPOINT
        self.SENT_MESSAGES_ENDPOINT=SENT_MESSAGES_ENDPOINT

    def read(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.MESSAGES_ENDPOINT + "?$filter=isRead eq false", headers=headers)
        # response = requests.get(self.GRAPH_API_BASE_URL + self.MESSAGES_ENDPOINT, headers=headers)
        if response.status_code == 200:
            emails_data = response.json().get('value', [])
            emails = []
            for email_data in emails_data:
                # Extracting email body and removing HTML tags using regex
                html_content = email_data.get('body', {}).get('content', '')
                text_content = re.sub(r'<[^>]*>', '', html_content)                
                email = {
                    'id': email_data.get('id'),
                    'subject': email_data.get('subject', ''),
                    'body': text_content,
                    "html_body":html_content,
                    'sender': email_data.get('sender', {}).get('emailAddress', {}).get('name', ''),
                    'sender_email': email_data.get('sender', {}).get('emailAddress', {}).get('address', ''),
                    'date': email_data.get('sentDateTime', ''),
                    'conversationId': email_data.get('conversationId', ""),
                    'torecipients':[each.get('emailAddress', {}).get('name', '') for each in email_data.get ('toRecipients',None)],
                }
                emails.append(email)               
            return emails
        else:
            return []

    def reply(self, mail_id, body: str, mail=None):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.token,
                'Content-Type': 'application/json'
            }

            reply_body = {
                'comment': body
            }

            reply_url = f"{self.GRAPH_API_BASE_URL}/me/messages/{mail_id}/reply"
            response = requests.post(reply_url, headers=headers, json=reply_body)

            if response.status_code == 202:
                print("Replied to the email with ID:", mail_id)
                return True
            else:
                print(f"Failed to reply to the email with ID '{mail_id}'. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"An error occurred while replying to the email with ID '{mail_id}': {e}")
            return False

    def get_related_emails_by_c_id(self, conversationID):
        emails_data = self.read_all()
        related_emails = [email for email in emails_data if email['conversationId'] == conversationID]

        emails_data_sent = self.read_all_sent()
        related_emails_sent = [email for email in emails_data_sent if email['conversationId'] == conversationID]

        all_related_emails = related_emails + related_emails_sent
        sorted_emails = sorted(all_related_emails, key=lambda x: x['date'])

        emails_with_structure = []

        for email in sorted_emails:
            print(dir(email))
            body = email.get('html_body', '')  # Use .get() to handle cases where 'body' might not exist
            sender = email.get('sender', '')  # Use .get() to handle cases where 'sender' might not exist
            date = email.get('date', '')  # Use .get() to handle cases where 'date' might not exist

            email_structure = {
                'sender': sender,
                'date': date,
                'body': body,
                'replies': []
            }
            print("-------------------------@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",body)

            # Check if the email has replies
            if 'replies' in email:
                for reply in email['replies']:
                    print(dir(reply))
                    reply_body = reply.get('html_body', '')
                    reply_sender = reply.get('sender', '')
                    reply_date = reply.get('date', '')

                    reply_structure = {
                        'sender': reply_sender,
                        'date': reply_date,
                        'body': reply_body
                    }

                    # Append reply to the email's replies list
                    email_structure['replies'].append(reply_structure)
                    print("email structure------------------------------------------------------------------",email_structure)

            emails_with_structure.append(email_structure)

        return emails_with_structure

    
    def get_related_emails(self, ID):
        emails_data=self.read_all()
        related_emails = [email for email in emails_data if email['id'] == ID]
        with open("mails.txt", 'w') as f:
            f.write(str(related_emails))
        return related_emails

    def read_all(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        # response = requests.get(self.GRAPH_API_BASE_URL + self.MESSAGES_ENDPOINT + "?$filter=isRead eq false", headers=headers)
        response = requests.get(self.GRAPH_API_BASE_URL + self.MESSAGES_ENDPOINT, headers=headers)
        if response.status_code == 200:
            emails_data = response.json().get('value', [])
            emails = []
            for email_data in emails_data:
                # Extracting email body and removing HTML tags using regex
                html_content = email_data.get('body', {}).get('content', '')
                text_content = re.sub(r'<[^>]*>', '', html_content)   
                email = {
                    'id': email_data.get('id'),
                    'subject': email_data.get('subject', ''),
                    'html_body':html_content,
                    'body': text_content,
                    'sender': email_data.get('sender', {}).get('emailAddress', {}).get('name', ''),
                    'sender_email': email_data.get('sender', {}).get('emailAddress', {}).get('address', ''),
                    'date': email_data.get('sentDateTime', ''),
                    'conversationId': email_data.get('conversationId', ""),
                    'torecipients':[each.get('emailAddress', {}).get('name', '') for each in email_data.get ('toRecipients',None)],
                }
                emails.append(email)               
            return emails
        else:
            return []
    
    def read_all_sent(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.SENT_MESSAGES_ENDPOINT ,headers=headers)
        if response.status_code == 200:
            emails_data = response.json().get('value', [])
            emails = []
            for email_data in emails_data:
                # print("---------------------------------------------------email data----------------------------",email_data)
                # Extracting email body and removing HTML tags using regex
                html_content = email_data.get('body', {}).get('content', '')
                text_content = re.sub(r'<[^>]*>', '', html_content)                
                email = {
                    'id': email_data.get('id'),
                    'subject': email_data.get('subject', ''),
                    'body': text_content,
                    'html_body':html_content,
                    'sender': email_data.get('sender', {}).get('emailAddress', {}).get('name', ''),
                    'sender_email': email_data.get('sender', {}).get('emailAddress', {}).get('address', ''),
                    'date': email_data.get('sentDateTime', ''),
                    'conversationId': email_data.get('conversationId', ""),
                    'torecipients':[each.get('emailAddress', {}).get('name', '') for each in email_data.get ('toRecipients',None)],
                }
                emails.append(email)               
            return emails
        else:
            return []