from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import json
import os

OPENAI_API_KEY="OPEN_AI_KEY"
os.environ["OPENAI_API_KEY"]=OPENAI_API_KEY

def get_details(mail_body,is_chain=False):
    if is_chain:
        class Calendar_specs(BaseModel):
            event_date: str = Field(description="The date of the event")
            event_time: str  = Field(description="The time of the event")
            event_name: str = Field(description="The description of the event")
            previous_event_time:str  = Field(description=" previously proposed event time")
            previous_event_date: str = Field(description=" previously proposed event date")

        json_parser = JsonOutputParser(pydantic_object=Calendar_specs)
        template = """You are an helpful assistant that assists in event planning and managing schedules, tasked to identify important details from a given context.

        Follow the below Instructions for completing the task.
        1. Understand the context provided thoroughly.
        2. Identify the details of any event or schedule provided.
        3. Strictly extract the details along with any date and time provided.
        4. If the event date and time are textual descriptions, kindly format them into date and time formats.
        5. Now, format the extracted content based on the format instructions provided.
        6. If any of the details are missing, return None for that particular detail.
        7. Handle reschedule messages by extracting the rescheduled date and time based on the given instructions.
        8. Identify reschedule messages like "tomorrow same time," "next week Monday," etc., by bringing in the current date element and extracting the rescheduled date.
        9. If rescheduling involves the same day with different time or same time next week, calculate based on the current date and time.
        10. If a relative time reference like "tomorrow," "next week," etc., is mentioned, use the previous event's date and time to calculate the updated date and time.
        11. Ensure that final reschedule confirmation properly reflects the updated date and time, and make sure it gets added to the Calendar correctly.

        Strictly follow the above instructions and return a valid JSON structure as expected and nothing more.


        The format Instructions are : {format_instructions}
        The input content is :{mail_conversation}.
        The Json output is :
        """
    else:
        class Calendar_specs(BaseModel):
            event_date: str = Field(description="The date of the event")
            event_time: str  = Field(description="The time of the event")
            event_name: str = Field(description="The description of the event")
        json_parser = JsonOutputParser(pydantic_object=Calendar_specs)
    
        template = """You are an helpful assistant that assists in event planning and managing schedules, tasked to identify important details from a given context.

        Follow the below Instructions for completing the task.
        1. Understand the context provided thoroughly.
        2. Identify the details of any event or schedule provided.
        3. Strictly extract the details along with any date and time provided.
        4. If the event date and time are textual descriptions, kindly format them into date and time formats.
        5. Now, format the extracted content based on the format instructions provided.
        6. If any of the details are missing, return None for that particular detail.
        7. Handle reschedule messages by extracting the rescheduled date and time based on the given instructions.
        8. Identify reschedule messages like "tomorrow same time," "next week Monday," etc., by bringing in the current date element and extracting the rescheduled date.
        9. If rescheduling involves the same day with different time or same time next week, calculate based on the current date and time.
        10. If a relative time reference like "tomorrow," "next week," etc., is mentioned, use the previous event's date and time to calculate the updated date and time.
        11. Ensure that final reschedule confirmation properly reflects the updated date and time, and make sure it gets added to the Calendar correctly.

        Strictly follow the above instructions and return a valid JSON structure as expected and nothing more.

        The format Instructions are : {format_instructions}
        The input content is :{mail_conversation}.
        The Json output is :
        """

    prompt = PromptTemplate(
        template=template,
        input_variables=["mail_conversation"],
        partial_variables={"format_instructions": json_parser.get_format_instructions()},
    )

    model= ChatOpenAI(openai_api_key=OPENAI_API_KEY)
    chain=LLMChain(prompt=prompt,llm=model)
    response=chain.invoke({"mail_conversation":mail_body})
    
    event_details=response["text"]
    details=json.loads(event_details)
    print(details)
    return details
