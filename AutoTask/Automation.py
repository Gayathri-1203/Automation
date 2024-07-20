import datetime       
from outlook_calendar import OutlookCalendar
from outlook_mail import EmailReader
from intent_classification import get_intent_of_mail
from EventDetailsExtractor import get_details
from mongodb import insert_appointment
import json
from datetime import timedelta
import datetime

class NewBooking:
    def __init__(self, customer_name, sender_name, appointment_date, appointment_time) -> None:
        self.subject = "Confirmation of Your Service Booking Request"
        self.body = f"""
        <html>
        <head>
            <style>
                /* Define styles for the header */
                .header-confirmation {{
                    background-color: #f2f2f2;
                    padding: 8px;
                    text-align: center;
                }}
                .header-confimation h1 {{
                    color: #333333;
                    font-family: Arial, sans-serif;
                }}
                .logo-confirmation {{
                    width: 250px;
                    height: 100px;
                }}
            </style>
        </head>
        <body>
            <div class="header-confimation">
                <img src="https://autotask.walkingtree.tech/static/autotask.png" class="logo-confirmation">
                <h1>Confirmation of Your Service Booking Request</h1>
            </div>

            <p>Dear <b>{customer_name},</b></p>

            <br>

            <p>To streamline the process, we propose the following date and time for your service appointment:</p>

            <br>

            <p><b>Date:</b> {appointment_date}<br><b>Time:</b> {appointment_time}</p>

            <br>

            <p>Please let us know if this suits your schedule. If not, kindly provide an alternative date and time that works for you. Additionally, if you have any specific requirements or preferences, feel free to share them with us.</p>

            <br>

            <p>Looking forward to serving you!</p>

            <br>

            <p>Best Regards,<br><b>{sender_name}</b><br>Customer Service Manager.</p>
        </body>
        </html>
        """


class RescheduleBooking:
    def __init__(self, customer_name, sender_name, appointment_date, appointment_time) -> None:
        self.subject = "Re: Service Appointment Rescheduling Request"
        self.body = f"""
        <html>
        <head>
            <style>
                /* Define styles for the header */
                .header-confirmation {{
                    background-color: #f2f2f2;
                    padding: 8px;
                    text-align: center;
                }}
                .header-confirmation h1 {{
                    color: #333333;
                    font-family: Arial, sans-serif;
                }}
                .logo-confirmation {{
                    width: 250px;
                    height: 100px;
                }}
            </style>
        </head>
        <body>
            <!-- Header with logo -->
            <div class="header-confirmation">
                <img src="https://autotask.walkingtree.tech/static/autotask.png" class="logo-confirmation">
                <h1>Re: Service Appointment Rescheduling Request</h1>
            </div>

        <p>Dear <b>{customer_name},</b></p>

        <br>

        <p>Thank you for reaching out to us to reschedule your service appointment.</p>

        <br>

        Proposed New Appointment:
       <p><b>Date:</b> {appointment_date}<br/><b>Time:</b> {appointment_time}</p>

       <br>
create
        <p>Please confirm if this new appointment works for you. If not, let us know your preferred date and time. We'll do our best to accommodate your schedule.</P

        <br>

        We appreciate your cooperation and understanding. Looking forward to serving you!

        <br>

        <p>Best Regards,<br/><b>{sender_name}</b><br/>Customer Service Manager.</p>
        """
            
class BookingConfirmation:
    def __init__(self, customer_name, sender_name, appointment_date, appointment_time) -> None:
        self.subject = "Confirmation of Your Upcoming Service Appointment"
        self.body = f"""
        <html>
        <head>
            <style>
                /* Define styles for the header */
                .header-confirmation {{
                    background-color: #f2f2f2;
                    padding: 8px;
                    text-align: center;
                }}
                .header-confirmation h1 {{
                    color: #333333;
                    font-family: Arial, sans-serif;
                }}
                .logo-confirmation {{
                    width: 250px;
                    height: 100px;
                }}
            </style>
        </head>
        <body>
            <div class="header-confirmation">
                <img src="https://autotask.walkingtree.tech/static/autotask.png" class="logo-confirmation">
                <h1>Confirmation of Your Upcoming Service Appointment</h1>
            </div>
        <p>Dear <b>{customer_name},</b></p>

        <br>

        <p>We're pleased to confirm your upcoming service appointment:</p>

        <br>

        <p><b>Date:</b> {appointment_date}<br/><b>Time:</b> {appointment_time}</p>

        <br>

        <p>If you have any specific instructions or requirements, please let us know in advance, and we'll do our best to accommodate them.</p>

        <br>

        <p>We appreciate your business and look forward to serving you.</p>

        <br>

        <p>Best Regards,<br/><b>{sender_name}</b><br/>Customer Service Manager.</p>
        </body>
        </html>
        """


class AutomationService:
    def __init__(self, mail_service: EmailReader, calendar_service: OutlookCalendar) -> None:
        self.mail_service = mail_service
        self.calendar_service = calendar_service
        self.processed_emails = set()

    def process_event_details(self,content:str,is_chain):
        event_details = get_details(mail_body=content,is_chain=is_chain)
        self.event_details=event_details
        if event_details["event_time"] and event_details["event_date"]:
            event_datetime=event_details["event_date"]+' '+event_details["event_time"]
            try:
                previous_datetime=event_details.get("previous_event_date",None)+" "+event_details.get("previous_event_time",None)
                return event_details["event_name"],event_datetime,previous_datetime
            except Exception as e:
                return event_details["event_name"],event_datetime,None
        else:
            None

    def process_mails(self):
        mails = self.mail_service.read()
        keyword = 'audit'
        if mails:
            for mail in mails:
                # Check if the email has already been processed
                if mail['id'] in self.processed_emails:
                    continue
                
                customer_name = mail["sender"]
                receiver_names = [recipient for recipient in mail['torecipients']]
                if keyword in (mail['subject']).lower() or keyword in mail['body'].lower():
                    related_mails_chain = self.mail_service.get_related_emails(ID=mail['id'])
                    if len(related_mails_chain) > 1:
                        is_chain = True
                    else:
                        is_chain = False
                    print("Chain ", is_chain)
                    for mail in related_mails_chain:
                        print(mail['body'])
                    print(related_mails_chain[0]['body'])
                    intent = get_intent_of_mail(body=related_mails_chain[0]['body'], is_chain=is_chain)

                    if processed_details := self.process_event_details(content=mail['body'], is_chain=is_chain):
                        event_name = processed_details[0]
                        event_datetime = processed_details[1]
                        previous_datetime = processed_details[2]
                        start_time, end_time = self.calendar_service.get_available_slots()
                        if intent == '1':
                            reply_mail = self.newBooking(mail=mail, customer_name=customer_name, receiver_names=receiver_names, event_name=event_name, event_datetime=self.calendar_service.format_event_time(event_datetime))
                            print(f"   New Booking : {reply_mail}")
                        elif intent == '2':
                            print("------------inside intent 2----------------")
                            reschedule_mail = self.reschedule(mail=mail, customer_name=customer_name, receiver_names=receiver_names, event_name=event_name, event_datetime=self.calendar_service.format_event_time(event_datetime), previous_datetime=self.calendar_service.format_event_time(previous_datetime))
                            print(f"  Rescheduling the booking : {reschedule_mail}")
                        elif intent == '3':
                            confirmation = self.confirmation(mail=mail, customer_name=customer_name, receiver_names=receiver_names, event_datetime=self.calendar_service.format_event_time(event_datetime))
                            print(f"  confirmation of meeting : {confirmation}")
                            # Add processed email to the set
                            self.processed_emails.add(mail['id'])
                            return mail
                    else:
                        pass
        else:
            print("No mails")


    def newBooking(self,mail,customer_name,receiver_names,event_name:str,event_datetime:datetime.datetime):
        new_booking_instance = NewBooking(customer_name, receiver_names[0], appointment_date=event_datetime.date(), appointment_time=event_datetime.time())
        reply_mail = self.mail_service.reply(mail_id=mail['id'], body=new_booking_instance.body)
        return reply_mail


    def reschedule(self,mail,customer_name,receiver_names,event_name,event_datetime:datetime.datetime,previous_datetime:datetime.datetime):
        reschedule_booking_instance = RescheduleBooking(customer_name, receiver_names[0], appointment_date=event_datetime.date(), appointment_time=event_datetime.time())
        event=self.calendar_service.get_event_by_start_time(start_time=previous_datetime)
        reply_mail = self.mail_service.reply(mail_id=mail['id'], body=reschedule_booking_instance.body)
        return reply_mail


    def confirmation(self, mail, customer_name, receiver_names, event_datetime: datetime):
        confirmation_booking_instance = BookingConfirmation(customer_name, receiver_names[0], appointment_date=event_datetime.date(), appointment_time=event_datetime.time())
        sender_email = mail['sender_email']
        sender_details = self.get_user_details_by_email(sender_email)
        print("Sender Email:", sender_email)
        print("Sender Details:", sender_details)
        if sender_details:
            event_id_sender = self.calendar_service.create_event_for_user(user_email=sender_email, 
                                                                        event_name="Service", 
                                                                        start_datetime=event_datetime, 
                                                                        end_datetime=event_datetime + timedelta(hours=1), 
                                                                        organizer_email=sender_email)
            if event_id_sender:
                print("Event created successfully in sender's calendar.")
                print("Event ID (Sender's Calendar):", event_id_sender)
                receiver_name=receiver_names[0]
                print("------------------receiver names-----------------",receiver_name)
                receiver_details = self.get_user_details(receiver_name)
                print("receoiver details are ------------",receiver_details)
                if receiver_details:
                    print("--------creating eventfor user-----------------------")
                    event_id_receiver = self.calendar_service.create_event_for_user(user_email=receiver_details["mail"], 
                                                                                    event_name="Service", 
                                                                                    start_datetime=event_datetime, 
                                                                                    end_datetime=event_datetime + timedelta(hours=1), 
                                                                                    organizer_email=sender_email)
                print("------------------------craeteing myevent------------")
                event_id_receiver = self.calendar_service.create_event(event_name="Service", 
                                                                        start_datetime=event_datetime)
                
                if event_id_receiver:
                    print(f"Event created successfully in {receiver_name}'s calendar.")
                    print(f"Event ID ({receiver_name}'s Calendar):", event_id_receiver)
                else:
                    print(f"Failed to create event in {receiver_name}'s calendar.")
                reply_mail = self.mail_service.reply(mail_id=mail['id'], body=confirmation_booking_instance.body)
                print("Confirmation email sent.")
                
                # Pass receiver details to create_appointment
                self.create_appointment(receiver_details,sender_details, event_datetime)
                return reply_mail
            else:
                print("Failed to create event in sender's calendar.")
                return None
        else:
            print("Failed to get user details for sender.")
            return None


    def create_appointment(self,sender_details, receiver_details, event_datetime):
        print("------------------------------------receiverdetails --------------------------------", receiver_details)
        if receiver_details:
            appointment_date_str = event_datetime.date().strftime('%Y-%m-%d')
            try:
                insert_appointment(
                    agent_name=f"{sender_details['givenName']} {sender_details['surname']}",
                    agent_id=sender_details['id'],
                    service='service appointment',
                    date=appointment_date_str,
                    conversation_id=['conversation_id'],
                    customer_name=receiver_details['displayName'],  # Change here
                    customer_mail=receiver_details['mail']
                )
                print("Appointment created successfully.")
                print("Agent Name:", f"{sender_details['givenName']} {sender_details['surname']}")
                print("Agent ID:", sender_details['id'])
                print("Service:", 'service appointment')
                print("Date:", appointment_date_str)
                print("Customer Name:", receiver_details['displayName'])  # Change here
                print("Customer Mail:", receiver_details['mail'])
            except Exception as e:
                print("An error occurred while inserting appointment:", str(e))
        else:
            print("Failed to create appointment.")




    def get_sender_email(self, sender_name):
        json_file_path = 'users.json'
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        user_data = data.get('value', [])
        for user in user_data:
            if user.get('displayName') == sender_name:
                return user.get('mail')
        return None
    def get_user_details_by_email(self, user_email):
        json_file_path = 'users.json'

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        user_data = data.get('value', [])
        for user in user_data:
            if user.get('mail') == user_email:
                return user
        return None

    def get_user_details(self, user_email):
        json_file_path = 'users.json'

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        user_data = data.get('value', [])
        for user in user_data:
            if user.get('displayName') == user_email:
                return user
        return None