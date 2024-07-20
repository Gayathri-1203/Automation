class NewBooking:
    def __init__(self,customer_name,sender_name, appointment_date,appointment_time) -> None:
        self.subject="Confirmation of Your Service Booking Request"
        self.body =f"""
Dear {customer_name},

Thank you for choosing our services! We have received your request for a new service booking, and we are eager to assist you.

To streamline the process, we propose the following date and time for your service appointment:

Date: {appointment_date}
Time: {appointment_time}
Please let us know if this suits your schedule. If not, kindly provide an alternative date and time that works for you. Additionally, if you have any specific requirements or preferences, feel free to share them with us.

Once we have your confirmation, we will ensure that everything is arranged according to your specifications. If you have any questions or need further assistance, please don't hesitate to reach out.

Looking forward to serving you!
Best Regards,
{sender_name}
Customer Service Manager.
        """
    
class RescheduleBooking:
    def __init__(self,customer_name,sender_name,appointment_date,appointment_time) -> None:
        self.subject="Re: Service Appointment Rescheduling Request"
        self.body=f"""
Dear {customer_name},
Thank you for getting in touch with us regarding the need to reschedule your upcoming service appointment.

We understand that plans can change, and we'll do our best to accommodate your request. Our team is currently reviewing the schedule, and we are pleased to provide you with an alternative date and time for your service appointment:

Proposed Date: {appointment_date}
Proposed Time: {appointment_time}
If the proposed date and time work for you, please confirm your availability. If not, or if you have any specific preferences or constraints, please let us know, and we'll do our best to work around them.

We appreciate your understanding and flexibility in this matter. We look forward to serving you on the updated schedule.
Best Regards,
{sender_name}
Customer Service Manager.
        """       
            
class BookingConfirmation:
    def __init__(self,customer_name,sender_name, appointment_date,appointment_time) -> None:
        self.subject=" Confirmation of Your Upcoming Service Appointment"
        self.body=f"""
Dear {customer_name},

Thank you for choosing our service needs. We are delighted to confirm your upcoming service appointment scheduled for:

Date: {appointment_date}
Time: {appointment_time}

Our team is fully committed to ensuring that you receive excellent service. If you have any specific instructions or requirements, please don't hesitate to inform us beforehand, and we will do our best to accommodate your needs.

Should you have any questions or if there are any changes needed, feel free to reach out to us at [Your Contact Information].

We appreciate your business and look forward to serving you.

Best Regards,
{sender_name}
Customer Service Manager.
        """       

from datetime import timedelta
import datetime
from outlook_calendar import OutlookCalendar
from outlook_mail import EmailReader
from intent_classification import get_intent_of_mail
from EventDetailsExtractor import get_details
class AutomationService:
    def __init__(self, mail_service: EmailReader, calendar_service: OutlookCalendar, customer_name, customer_email) -> None:
        self.mail_service = mail_service
        self.calendar_service = calendar_service
        self.customer_name = customer_name
        self.customer_email = customer_email
    
    def process_event_details(self,content:str,is_chain):
        event_details = get_details(mail_body=content,is_chain=is_chain)
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
            print("================================mails========================",mails)
            for mail in mails:
                customer_name = mail["sender"]
                receiver_names = [recipient for recipient in mail['torecipients']]
                if keyword in (mail['subject']).lower() or keyword in mail['body'].lower():
                    reply=None
                    print(f"sent from {customer_name}  to {receiver_names}  body is {mail['body']}")
                    # Check intent and send reply
                    related_mails_chain=self.mail_service.get_related_emails(original_email_id=mail['id'])
                    if len(related_mails_chain)>1:
                        is_chain=True
                    else:
                        is_chain=False
                    print("Chain ",is_chain)
                    for mail in related_mails_chain:
                        print(mail['body'])
                    print(related_mails_chain)
                    print(related_mails_chain[-1]['body'])
                    intent = get_intent_of_mail(body=related_mails_chain[-1]['body'],is_chain=is_chain)

                    if processed_details:=self.process_event_details(content=mail['body'],is_chain=is_chain):
                        event_name=processed_details[0]
                        event_datetime=processed_details[1]
                        previous_datetime=processed_details[2]
                        start_time,end_time=self.calendar_service.get_available_slots()
                        if intent == '1':
                            # For new booking
                            reply_mail = self.newBooking(mail=mail,customer_name=customer_name,receiver_names=receiver_names,event_name=event_name,event_datetime=self.calendar_service.format_event_time(event_datetime))
                            print(f"   New Booking : {reply_mail}")
                        elif intent == '2':
                            # For rescheduling
                            reply_mail = self.reschedulereschedule=self.reschedule(mail=mail,customer_name=customer_name,receiver_names=receiver_names,event_name=event_name,event_datetime=self.calendar_service.format_event_time(event_datetime),previous_datetime=self.calendar_service.format_event_time(previous_datetime))
                            print(f"  Rescheduling the booking : {reply_mail}")
                        elif intent == '3':
                            # For confirmation
                            reply_mail = self.confirmation(mail=mail,customer_name=customer_name,receiver_names=receiver_names,event_datetime=self.calendar_service.format_event_time(event_datetime))
                            print(f"  Confirmation of meeting : {reply_mail}")
                    else:
                        # event date is missing
                        pass
        else:
            print("No mails")

    def newBooking(self, mail, customer_name, receiver_names, event_name: str, event_datetime: datetime):
        # Convert the event_datetime to a naive datetime object
        event_datetime_naive = event_datetime.replace(tzinfo=None)

        new_booking_instance = NewBooking(customer_name, receiver_names[0], appointment_date=event_datetime_naive.date(), appointment_time=event_datetime_naive.time())
        reply_mail = self.mail_service.reply(mail_id=mail['id'], body=new_booking_instance.body)
        return reply_mail

    def reschedule(self, mail, customer_name, receiver_names, event_name, event_datetime: datetime.datetime):
        event_datetime_naive = event_datetime.replace(tzinfo=None)
        reschedule_booking_instance = RescheduleBooking(customer_name, receiver_names[0], appointment_date=event_datetime.date(), appointment_time=event_datetime.time())
        reply_mail = self.mail_service.reply(mail_id=mail['id'], body=reschedule_booking_instance.body)
        return reply_mail

    def confirmation(self, mail, customer_name, receiver_names, event_datetime: datetime.datetime):
        # Assuming you have a method to create events in the calendar service
        event_id = self.calendar_service.create_event(event_name="Service Appointment", start_datetime=event_datetime)
        if event_id:
            print("Event created successfully.")
            # Send confirmation email to the customer
            booking_confirmation_instance = BookingConfirmation(customer_name, receiver_names[0], appointment_date=event_datetime.date(), appointment_time=event_datetime.time())
            reply_mail = self.mail_service.reply(mail_id=mail['id'], body=booking_confirmation_instance.body)
            print("Confirmation email sent.")
            return reply_mail
        else:
            print("Failed to create event.")
            # Handle failure to create event, perhaps send a notification to admin
            return None

