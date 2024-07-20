from outlook_calendar import OutlookCalendar
from outlook_mail import EmailReader
from Automation import AutomationService
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time


def automate(token,GRAPH_API_BASE_URL,MESSAGES_ENDPOINT,EVENTS_ENDPOINT,SENT_MESSAGES_ENDPOINT):
    print("--------------------------------------------------------token--------------------------",token)
    service=AutomationService(mail_service=EmailReader(token=token,GRAPH_API_BASE_URL=GRAPH_API_BASE_URL,MESSAGES_ENDPOINT=MESSAGES_ENDPOINT,SENT_MESSAGES_ENDPOINT=SENT_MESSAGES_ENDPOINT),calendar_service=OutlookCalendar(token=token,GRAPH_API_BASE_URL=GRAPH_API_BASE_URL,EVENTS_ENDPOINT=EVENTS_ENDPOINT))

    while True:
        print("-"*10)
        mail=service.process_mails()
        events = service.calendar_service.read_events()
        if events:
            print("-------------------------")
        time.sleep(5)