
# Your existing imports and code...
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import datetime
from flask_cors import CORS
from flask_apscheduler import APScheduler
import json
import math
from googletrans import Translator
import asyncio
load_dotenv()

app = Flask(__name__)
CORS(app)

highalert = set()
def main(input_text):
    genai.configure(api_key=os.getenv('API_KEY'))
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(input_text)
    return response.text  # synchronous return



@app.route('/index.html')
def index():
    
    return render_template('try.html')  # Make sure try.html is in your templates folder

@app.route('/process', methods=['POST'])

@app.route('/process', methods=['POST'])

def process():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response_text = main('u ARE A BOT THAT IS BUILT FOR HELPING PEOPLE IN EARTHQUAKE U R AN VOICE ASSISTANT YOU WILL ALWAYS REPLY OTHERS QUESTIONS IN HELPING TONE WITHOUT PUNCTUATIONS LIKE ASTERIKS ETC AND ALSO UR ANSWER WILL BE MAXIMUM 2 LINES always say in order to find safe places refer to the save zone map in the end THIS WAS TEH INSTRUCTIONS DONT REPLY ON THIS NOW U R GIVEN THE USERS QUESTION AS THIS:'+user_input)
    return jsonify({"response": response_text})



def fetch_earthquake_data():
    URL = "https://deprem.afad.gov.tr/EventData/GetEventsByFilter"
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=1)

    event_filter = {
        "EventSearchFilterList": [
            {"FilterType": 8, "Value": start_date.isoformat()},
            {"FilterType": 9, "Value": end_date.isoformat()},
        ],
        "Skip": 0,
        "Take": 100,
        "SortDescriptor": {"field": "eventDate", "dir": "desc"},
    }

    response = requests.post(URL, json=event_filter)
    data = response.json()
    return data.get('eventList', [])



def check_and_trigger_chatbot():
    new_alerts = []
    events = fetch_earthquake_data()
    for event in events:
        mag = event.get('magnitude', 0)
        loc = event.get('location', 'Unknown')
        if mag > 3.0 and loc not in highalert:
            highalert.add(loc)
            response = f"Dikkat! {loc} bölgesinde {mag} büyüklüğünde bir deprem meydana geldi."
            print("Alert Triggered:", response)
            new_alerts.append({
                "location": loc,
                "magnitude": mag,
                "message": response
            })
    return new_alerts


@app.route('/earthquakes')
def get_earthquakes():
    new_alerts = check_and_trigger_chatbot()
    return jsonify({"new_alerts": new_alerts})

@app.route('/test_trigger')
def test_trigger():
    fake_events = [{
        "magnitude": 3.5,
        "location": "Test Location",
        "longitude": 30.0,
        "latitude": 40.0,
        "eventDate": datetime.datetime.now().isoformat()
    }]
    alerts = []
    for event in fake_events:
        mag = event['magnitude']
        loc = event['location']
        if mag > 2.0 and loc not in highalert:
            highalert.add(loc)

            alert_message = f"Earthquake alert! Magnitude {mag} at {loc}"
            chatbot_response = alert_message

            alerts.append({
                "event": event,
                "chatbot_response": chatbot_response
            })
            print(f"Chatbot Alert: {chatbot_response}")
    return jsonify({"message": "Test trigger ran", "alerts_triggered": alerts})


class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

scheduler.add_job(id='Check Earthquakes', func=check_and_trigger_chatbot, trigger='interval', seconds=60)


if __name__ == '__main__':
    app.run(debug=True)
