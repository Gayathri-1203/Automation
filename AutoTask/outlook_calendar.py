import os
import requests
from dotenv import load_dotenv
from flask import session
from datetime import datetime, timedelta
import pytz
import json
import pytz
from datefinder import find_dates
from typing import Optional


class OutlookCalendar:
    def __init__(self, token, GRAPH_API_BASE_URL, EVENTS_ENDPOINT):
        self.token = token
        self.GRAPH_API_BASE_URL = GRAPH_API_BASE_URL
        self.EVENTS_ENDPOINT = EVENTS_ENDPOINT
        self.time_slots = [
            datetime.time(datetime.strptime("09:00", "%H:%M")),
            datetime.time(datetime.strptime("12:00", "%H:%M")),
            datetime.time(datetime.strptime("15:00", "%H:%M"))
        ]
    
    def format_event_time(self, datetime_obj: str) -> Optional[datetime]:
        if isinstance(datetime_obj, str):
            found_dates = list(find_dates(datetime_obj))
            if found_dates:
                timezone = pytz.timezone("UTC")
                localized_datetime = timezone.localize(found_dates[0])
                return localized_datetime
        return None


    def create_event(self, start_datetime: datetime, event_name: str) -> bool:
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}

        start_datetime_naive = start_datetime.replace(tzinfo=None)

        user_timezone = pytz.timezone('Asia/Kolkata')

        start_datetime_local = user_timezone.localize(start_datetime_naive)
        end_datetime_local = start_datetime_local + timedelta(hours=1)

        data = {
            'subject': event_name,
            'start': {
                'dateTime': start_datetime_local.isoformat(),
                'timeZone': user_timezone.zone
            },
            'end': {
                'dateTime': end_datetime_local.isoformat(),
                'timeZone': user_timezone.zone
            }
        }

        try:
            response = requests.post(self.GRAPH_API_BASE_URL + self.EVENTS_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()
            print("Event created successfully.")
            return True
        except requests.exceptions.RequestException as e:
            print("Error creating event:", e)
            return False

    def create_event_for_user(self, user_email, event_name, start_datetime, end_datetime, organizer_email=None):
        url = f"{self.GRAPH_API_BASE_URL}users/{user_email}/events"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        start_datetime_naive = start_datetime.replace(tzinfo=None)

        user_timezone = pytz.timezone('Asia/Kolkata')

        start_datetime_local = user_timezone.localize(start_datetime_naive)

        end_datetime_local = start_datetime_local + timedelta(hours=1)

        data = {
            "subject": event_name,
            "start": {"dateTime": start_datetime_local.isoformat(), "timeZone": user_timezone.zone},
            "end": {"dateTime": end_datetime_local.isoformat(), "timeZone": user_timezone.zone},
            "organizer": {"emailAddress": {"address": organizer_email}},
            "attendees": [{"emailAddress": {"address": user_email}}]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return response.json().get('id')
        else:
            print("Failed to create event:", response.text)
        return None

        
    def read_events(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.EVENTS_ENDPOINT, headers=headers)

        if response.status_code == 200:
            events_data = response.json().get('value', [])
            events = []
            for event_data in events_data:
                start_time_str = event_data.get('start', {}).get('dateTime', '')
                end_time_str = event_data.get('end', {}).get('dateTime', '')
                start_time = self.format_event_time(start_time_str)
                end_time = self.format_event_time(end_time_str)

                event = {
                    'id': event_data.get('id'),
                    'subject': event_data.get('subject', ''),
                    'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': event_data.get('location', {}).get('displayName', ''),
                    'organizer': event_data.get('organizer', {}).get('emailAddress', {}).get('name', ''),
                    'attendees': [attendee.get('emailAddress', {}).get('name', '') for attendee in event_data.get('attendees', [])],
                    'description': event_data.get('body', {}).get('content', ''),
                }
                events.append(event)

            with open("calendar_events.json", "w") as json_file:
                json.dump(events, json_file, indent=4)
                
            return events
        else:
            return []


    def read_events_for_user(self, user_email):
        url = f"{self.GRAPH_API_BASE_URL}users/{user_email}/calendar/events"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            events_data = response.json().get('value', [])
            events = []
            for event_data in events_data:
                start_time_str = event_data.get('start', {}).get('dateTime', '')
                end_time_str = event_data.get('end', {}).get('dateTime', '')
                start_time = self.format_event_time(start_time_str)
                end_time = self.format_event_time(end_time_str)

                event = {
                    'id': event_data.get('id'),
                    'subject': event_data.get('subject', ''),
                    'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': event_data.get('location', {}).get('displayName', ''),
                    'organizer': event_data.get('organizer', {}).get('emailAddress', {}).get('name', ''),
                    'attendees': [attendee.get('emailAddress', {}).get('name', '') for attendee in event_data.get('attendees', [])],
                    'description': event_data.get('body', {}).get('content', ''),
                }
                events.append(event)

            with open(f"{user_email}_calendar_events.json", "w") as json_file:
                json.dump(events, json_file, indent=4)

            return events
        else:
            print(f"Failed to read events for {user_email}: {response.text}")
            return []



    def read_events(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.EVENTS_ENDPOINT, headers=headers)

        if response.status_code == 200:
            events_data = response.json().get('value', [])
            events = []
            for event_data in events_data:
                start_time_str = event_data.get('start', {}).get('dateTime', '')
                end_time_str = event_data.get('end', {}).get('dateTime', '')
                start_time = self.format_event_time(start_time_str)
                end_time = self.format_event_time(end_time_str)

                event = {
                    'id': event_data.get('id'),
                    'subject': event_data.get('subject', ''),
                    'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': event_data.get('location', {}).get('displayName', ''),
                    'organizer': event_data.get('organizer', {}).get('emailAddress', {}).get('name', ''),
                    'attendees': [attendee.get('emailAddress', {}).get('name', '') for attendee in event_data.get('attendees', [])],
                    'description': event_data.get('body', {}).get('content', ''),
                }
                events.append(event)

            with open("others_calendar_events.json", "w") as json_file:
                json.dump(events, json_file, indent=4)
                
            return events
        else:
            return []
        

    def get_event_by_start_time(self, start_time):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.EVENTS_ENDPOINT, headers=headers)

        if response.status_code == 200:
            events_data = response.json().get('value', [])
            for event_data in events_data:
                start_time_str = event_data.get('start', {}).get('dateTime', '')
                event_start_time = self.format_event_time(start_time_str)
                if event_start_time == start_time:
                    return event_data
        return None

    def get_events_after_current_time(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.GRAPH_API_BASE_URL + self.EVENTS_ENDPOINT, headers=headers)
        
        if response.status_code == 200:
            events_data = response.json().get('value', [])
            current_time = datetime.now(pytz.utc)
            upcoming_events = []
            for event_data in events_data:
                start_time_str = event_data.get('start', {}).get('dateTime', '')
                start_time = self.format_event_time(start_time_str)
                if start_time > current_time:
                    upcoming_events.append(event_data)
            return upcoming_events
        else:
            print("Failed to retrieve events.")
            return []

    def get_event_by_subject(self, subject):
        events = self.get_events_after_current_time()
        for event_data in events:
            if event_data.get('subject', '') == subject:
                return event_data
        return None
    
        
    def get_available_slots(self, days_delta=2):
        if days_delta > 5:
            return None

        start_date = datetime.now(pytz.utc).date() + timedelta(days=days_delta)
        for each in self.time_slots:
            slot_start = datetime.combine(start_date, datetime.strptime(f"{each.hour:02d}:00", "%H:%M").time()).replace(tzinfo=pytz.utc)
            slot_end = datetime.combine(start_date, datetime.strptime(f"{each.hour+1:02d}:00", "%H:%M").time()).replace(tzinfo=pytz.utc)
            if self.event_doesnot_exists_at_time(start_datetime=slot_start, end_datetime=slot_end):
                return slot_start, slot_end

        return self.get_available_slots(days_delta=days_delta + 1)



    def event_doesnot_exists_at_time(self, start_datetime: datetime, end_datetime: datetime) -> bool:
        events = self.get_events_after_current_time()
        for event_data in events:
            start_time_str = event_data.get('start', {}).get('dateTime', '')
            end_time_str = event_data.get('end', {}).get('dateTime', '')
            event_start_time = self.format_event_time(start_time_str)
            event_end_time = self.format_event_time(end_time_str)
            if start_datetime < event_end_time and end_datetime > event_start_time:
                return False
        return True


