import identity
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for,jsonify
from flask_session import Session
from functools import wraps
import os
import app_config
import threading
import json
from outlook_calendar import OutlookCalendar
from mongodb import read_appointments
from outlook_mail import EmailReader
from service import automate

app = Flask(__name__, static_folder="./static")
app.config.from_object(app_config)
Session(app)
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")

print("CLIENT_ID:", CLIENT_ID)
print("CLIENT_SECRET:", CLIENT_SECRET)
print("TENANT_ID:", TENANT_ID)


from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
)

MESSAGES_ENDPOINT = "/me/mailFolders/inbox/messages"
SENT_MESSAGES_ENDPOINT = "/me/mailFolders/sentitems/messages"

GRAPH_API_BASE_URL = 'https://graph.microsoft.com/v1.0/'
EVENTS_ENDPOINT = 'me/calendar/events'
ALL_THREADS = []

def background_process(token):
    print("----------------in background process----------------")
    access_token = token["access_token"]
    automate(token=access_token, GRAPH_API_BASE_URL=GRAPH_API_BASE_URL, MESSAGES_ENDPOINT=MESSAGES_ENDPOINT,
             EVENTS_ENDPOINT=EVENTS_ENDPOINT, SENT_MESSAGES_ENDPOINT=SENT_MESSAGES_ENDPOINT)

def start_background_thread(token):
    thread = threading.Thread(target=background_process, args=(token,))
    thread.start()
    ALL_THREADS.append(thread)

@app.route("/")
def login():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        return render_template('config_error.html')
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=app_config.SCOPES,
        redirect_uri=url_for("auth_response", _external=True),
    ))

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("login", _external=True)))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth.get_user():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/index")
@login_required
def index():
    token = auth.get_token_for_user(app_config.SCOPES)
    session['token'] = token['access_token']
    print("Token:", token)
    start_background_thread(token)
    return render_template('homepage.html', user=auth.get_user(), version=identity.__version__)


@app.route("/call_downstream_api")
@login_required
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPES)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    with open('users.json','w' ) as f:
        json.dump(api_result,f)
    session['token'] = token['access_token']
    return render_template('display.html', result=api_result)


@app.route('/homepage')
@login_required
def homepage():
    mails= 0
    appointments=3
    meetings= 1
    return render_template('homepage.html',mails=mails,appointments=appointments,meetings=meetings)

@app.route('/appointments')
@login_required
def appointments():
    appointments_data = read_appointments()
    print("Appointments Data:", appointments_data)
    return render_template('appointments.html', appointments=appointments_data)

@app.route('/mails')
@login_required
def mails():
    token = session.get('token')
    mail_reader = EmailReader(token=token, GRAPH_API_BASE_URL=GRAPH_API_BASE_URL, MESSAGES_ENDPOINT=MESSAGES_ENDPOINT, SENT_MESSAGES_ENDPOINT=SENT_MESSAGES_ENDPOINT)
    mails = mail_reader.read_all()
    print("-----------mails-------",len(mails))
    # Group emails by conversation ID
    grouped_emails = {}
    for email in mails:
        conversation_id = email['conversationId']
        if conversation_id not in grouped_emails:
            grouped_emails[conversation_id] = []
        grouped_emails[conversation_id].append(email)
    
    print("-----------groupedmails-------",len(grouped_emails))
    # Find the first email in each conversation
    first_emails = []
    for conversation_id, emails_in_group in grouped_emails.items():
        first_email = min(emails_in_group, key=lambda x: x['date'])
        first_emails.append(first_email)
    
    print("-----------firstmails-------",len(first_emails))
    return render_template('mails.html', mails=first_emails)


@app.route('/get_events')
@login_required
def events_data():
    print("--------getting events-----------")
    token = session.get('token')
    
    # Read events for the user
    my_events = OutlookCalendar(token=token, GRAPH_API_BASE_URL=GRAPH_API_BASE_URL, EVENTS_ENDPOINT=EVENTS_ENDPOINT).read_events()
  
    user_email = "bhashkar.dev@walkingtree.technology"
 
    # Read events for a specific user
    events_of_user = OutlookCalendar(token=token, GRAPH_API_BASE_URL=GRAPH_API_BASE_URL, EVENTS_ENDPOINT=EVENTS_ENDPOINT).read_events_for_user(user_email)
    
    print("My Events:", len(my_events))
    print("User's Events:", len(events_of_user))
    
    return jsonify({"my_events": my_events, "user_events": events_of_user})


@app.route('/calendar')
@login_required
def calendar_data():
    return render_template('calendar.html')


@app.route("/mail/<convo_id>")
@login_required
def conversation_thread(convo_id):
    print("--------------conversation--------------")
    print(convo_id)
    token = session.get('token')
    mail_reader = EmailReader(token=token, GRAPH_API_BASE_URL=GRAPH_API_BASE_URL, MESSAGES_ENDPOINT=MESSAGES_ENDPOINT, SENT_MESSAGES_ENDPOINT=SENT_MESSAGES_ENDPOINT)
    mails = mail_reader.get_related_emails_by_c_id(conversationID=convo_id)
    print("-------------------------mails------------------------------------------",mails)
    return render_template('conversation.html', mails=mails)


if __name__ == "__main__":
    print("-------------------running-------------",ALL_THREADS)
    for thread in ALL_THREADS:
        print(thread)
    
    app.run(host="0.0.0.0",port=5000,debug=True)

