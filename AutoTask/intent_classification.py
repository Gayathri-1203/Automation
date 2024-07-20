from langchain.schema import HumanMessage,SystemMessage
from langchain_openai.chat_models import ChatOpenAI
import os

OPENAI_API_KEY=""
os.environ["OPENAI_API_KEY"]=OPENAI_API_KEY

def get_intent_of_mail(body,is_chain=False):
    if is_chain:
        SYSTEM_TEMPLATE = """"
        You possess the skill to deduce intent from context and are assigned to identify the intent of user's reply within a chain of messages.

        Follow the below instructions for completing the task:

        1. Identify the users reply from the given mail reply chain. (The latest user's reply is always on the top of the chain)
        2. Identify the intent of the users reply content that is presenton the top.
        3. For better understanding could refer to the original mail in the chain of mails to which the reply intended to. 
        4. Only return the numerical value from given below and nothing else.

        Now, based on intention of the user, classify it under one of the below categories depending on what is being asked for
            1. new booking request or request for a new service
            2. Request for rescheduling of the previously created booking request or updating the timing of an existing event 
            3. Confirmation of the Booking or confirmation of the created event or confirmation of the appointment

        Based on the above category the intent belongs-to, stictly return the numerical value of that category. 
        The numerical category of the intent is :"""
    else:
        SYSTEM_TEMPLATE = """
        You possess the skill to deduce intent from context and are assigned to identify the intent of user's mail content.

        Follow the below instructions for completing the task:
                
        1. Identify the intent of the users given content.
        2. Only return the numerical value from given below and nothing else.
                
            Now, based on intention of the user, classify it under one of the below categories depending on what is being asked for
                1. New booking request or request for a new service
                2. Request for rescheduling of the previously created booking request or updating the timing of an existing event 
                3. Confirmation of the Booking
                    
        Based on the above category identified, stictly return the numerical value of the category.
        The numerical category of the intent is :"""

    print("        Asking     GPT       ")
    llm=ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo")
    messages=[SystemMessage(content=SYSTEM_TEMPLATE),HumanMessage(content=f"Email body content: {body}")]
    res = llm.invoke(messages).content

    if res=="1":
        print("             New booking")
    elif res=="2":
        print("             Re-Schedule")
    elif res=="3":
        print("             Confirmation")
    return res