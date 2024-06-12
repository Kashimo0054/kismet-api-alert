import requests
import json
import time
import winsound
from twilio.rest import Client

# Configuration for the Kismet API
url = "http://username:password@192.168.100.28:2501/alerts/all_alerts.json"
payload = {}

# Twilio configuration
account_sid = 'Your-twilio-sid'
auth_token = 'Your-twilio-authtoken'
twilio_client = Client(account_sid, auth_token)
twilio_from_number = 'your-twilio-from_number'
twilio_to_number = 'your-recepient-number'

previous_alerts = []

def fetch_alerts():
    response = requests.get(url, data=payload)
    return response.json()

def get_new_alerts(current_alerts, previous_alerts):
    current_alerts_set = set(json.dumps(alert) for alert in current_alerts)
    previous_alerts_set = set(json.dumps(alert) for alert in previous_alerts)
    new_alerts_set = current_alerts_set - previous_alerts_set
    new_alerts = [json.loads(alert) for alert in new_alerts_set]
    return new_alerts

def beep_sound():
    duration = 1000  # milliseconds
    freq = 100  # Hz (A4 note)
    for _ in range(10):
        winsound.Beep(freq, duration)

while True:
    try:
        current_alerts = fetch_alerts()
        new_alerts = get_new_alerts(current_alerts, previous_alerts)
        if new_alerts:
            print(f"New alerts found: {len(new_alerts)}")
            for alert in new_alerts:
                short_message = json.dumps(alert)[:1000]  # Extracting first 1000 characters of JSON alert 
                message = twilio_client.messages.create(
                    from_=twilio_from_number,
                    body=short_message,
                    to=twilio_to_number
                )
                print(f"SMS sent with SID: {message.sid}")
            beep_sound()
            # Update previous alerts to current alerts
            previous_alerts = current_alerts
        else:
            print("No new alerts.")
        
        # Poll every 10 seconds
        time.sleep(10)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(10)
