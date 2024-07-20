from pymongo import MongoClient

appointment_client = MongoClient('mongodb://localhost:27017')
appointment_db = appointment_client['appointment_db']
appointment_collection = appointment_db['appointments']

def insert_appointment(agent_name, agent_id, service, date, customer_name, customer_mail, conversation_id):    
    appointment_data = {
        "agent_name": agent_name,
        "agent_id": agent_id,
        "service": service,
        "date": date,
        "customer_name": customer_name,
        "customer_mail": customer_mail,
        "conversation_id": conversation_id
    }
    try:
        result = appointment_collection.insert_one(appointment_data)
        inserted_id = result.inserted_id
        print("Inserted ID:=============================================================================================", inserted_id)
    except Exception as e:
        print("An error occurred while inserting appointment:", str(e))

def read_appointments():
    appointment_list = list(appointment_collection.find())
    return appointment_list
