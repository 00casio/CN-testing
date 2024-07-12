"""
Description:
    This script sets up a Flask web application to handle AMF and SMF notifications,
    registers callback functions for various events, and updates MongoDB collections
    with received notifications.

Requirements:
    - Flask
    - pymongo
    - requests

Usage:
    - Run the script to start the Flask web application.
    - Incoming AMF notifications are handled at '/callbacks/amf-reports' endpoint.
    - Incoming SMF notifications are handled at '/callbacks/dataplane-reports' endpoint.

How to Use:
    1. Ensure all required packages are installed.
    2. Run the script.
    3. The Flask application will start, listening on the specified host and port.

"""
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, 'modules'))
sys.path.append(os.path.join(parent_dir, 'subscriptions_manager'))

import callbacks as callbacks
import signal
import requests
import subprocess
from flask import Flask, request
from pymongo import MongoClient , errors
import subscriptions as subscriptions
import logging
import json
import importlib
import yaml
from yaml.loader import SafeLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
config_file_path = os.path.join(parent_dir, 'etc', 'configuration.yaml')
status_file_path = os.path.join(current_dir, '../../etc/handler_status.yaml')

with open(config_file_path, 'r') as f:
    data = yaml.load(f, Loader=SafeLoader)

sbi_addr = data['sbi']['ip']
sbi_port    = data['sbi']['port']

amf_addr= data['amf_1']['ip']
amf_url = data['amf_1']['url']
amf_port= data['amf_1']['port']

smf_addr= data['smf_1']['ip']
smf_url = data['smf_1']['url']
smf_port= data['smf_1']['port']


changed_status_dict = {}

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
logging.getLogger('pymongo').setLevel(logging.INFO)
logging.getLogger("docker.utils.config").setLevel(logging.INFO)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.DEBUG)


def check_mongodb_status():
    try:
        # Run the 'systemctl is-active mongod' command
        result = subprocess.run(['systemctl', 'is-active', 'mongod'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if MongoDB is active
        if result.stdout.strip() == 'active':
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

mongodb_status=check_mongodb_status() 
if  mongodb_status==False :
    with open(status_file_path, 'r') as file:
        data = yaml.safe_load(file)
    data['handler_status'] = 'off'  
    data['handler_pid'] = 'None' 
    with open(status_file_path, 'w') as file:
        yaml.safe_dump(data, file)
    
    assert False,  "Could not connect to MongoDB"

client = MongoClient('mongodb://localhost:27017/')
db = client['notification_db']
amf_collection = db['amf_notifications']
smf_collection = db['smf_notifications']
log.info("Successfully connected to MongoDB.")




# Initialize MongoDB collections


# Clean collections
def clean_collections():
    amf_collection.delete_many({})
    smf_collection.delete_many({})
    log.info("Collections cleaned.")
    
clean_collections()
# Initialize subscriptions
log.info("Subscribing to Registration Events from AMF")
amf_endpoint = subscriptions.get_amf_subscription_url(amf_addr , amf_port , amf_url)
amf_sub = subscriptions.create_amf_subscription(amf_endpoint , sbi_addr , sbi_port)
log.info("Subscribing to User Sessions Events from SMF")

smf_endpoint = subscriptions.get_smf_subscription_url(smf_addr , smf_port , smf_url)
smf_sub = subscriptions.create_smf_subscription(smf_endpoint , sbi_addr , sbi_port )


if amf_sub == "" or smf_sub == "":
    log.error("Subscription to CN events failed... Exiting \n check AMF and SMF connectivity")
    with open(status_file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    data['handler_status'] = 'off'  
    data['handler_pid'] = 'None' 
    with open(status_file_path, 'w') as file:
        yaml.safe_dump(data, file)
        
    assert False, "Subscription to CN events failed"

def connected_ues():

    existing_users = {}

    for document in amf_collection.find():
        for report in document["reportList"]:
            supi = report["supi"]
            ran_ue_ngap_id = report["ranUeNgapId"]
            rm_state = report["rmInfoList"][0]["rmState"]
            timestamp = report["timeStamp"]

            if supi in existing_users:
                if timestamp > existing_users[supi]['timestamp']:
                    existing_users[supi] = {'supi': supi, 'ran_ue_ngap_id': ran_ue_ngap_id, 'rm_state': rm_state, 'timestamp': timestamp}
            else:
                existing_users[supi] = {'supi': supi, 'ran_ue_ngap_id': ran_ue_ngap_id, 'rm_state': rm_state, 'timestamp': timestamp}

    keys_to_remove = []
    
    for supi, user_info in existing_users.items():
        if user_info['rm_state'] != "REGISTERED":
            keys_to_remove.append(supi)

    for key in keys_to_remove:
        existing_users.pop(key)
    
    return existing_users

# handle the callbacks for registered UEs
def handle_registered_ue_callbacks():
    events_json_path = os.path.join(current_dir, '../modules/events.json')
    with open(events_json_path, 'r') as json_file:
        data = json.load(json_file)
    registered_users = connected_ues()

    if data["events"]["RegisteredUEs"]["callbacks"] and registered_users:
        last_registered_user = list(registered_users.values())[-1]
        for callback_name in data["events"]["RegisteredUEs"]["callbacks"]:
            callback_function = getattr(callbacks, callback_name, None)
            if callback_function:
                callback_function(last_registered_user)

def handle_changed_status_callbacks():
    global changed_status_dict
    latest_status_dict = {}

    for document in amf_collection.find():
        for report in document["reportList"]:
            supi = report["supi"]
            ran_ue_ngap_id_amf = report["ranUeNgapId"]
            rm_state_amf = report["rmInfoList"][0]["rmState"]
            timestamp = report["timeStamp"]

            if supi not in latest_status_dict or timestamp > latest_status_dict[supi]['timestamp_amf']:
                latest_status_dict[supi] = {
                    'supi': supi,
                    'ranUeNgapId_amf': ran_ue_ngap_id_amf,
                    'rmState_amf': rm_state_amf,
                    'timestamp_amf': timestamp
                }

    for supi, status in latest_status_dict.items():
        if supi in changed_status_dict:
            if status['rmState_amf'] != changed_status_dict[supi]['rmState_amf']:
                temp_dict = {supi: status}

                home_dir = os.path.expanduser("~")
                events_json_path = os.path.join(home_dir, '5gcsdk', 'src', 'modules', 'events.json')

                with open(events_json_path, 'r') as json_file:
                    data = json.load(json_file)

                if data["events"]["UEStatus"]["callbacks"]:
                    for callback_name in data["events"]["UEStatus"]["callbacks"]:
                        callback_function = getattr(callbacks, callback_name, None)
                        if callback_function:
                            callback_function(temp_dict)

        changed_status_dict[supi] = status

# Route for AMF notifications
@app.route('/callbacks/amf-reports', methods=['POST'])
def receive_amf_notification():
    if request.method == 'POST':
        content = request.get_json(force=True)
        log.debug(content)
        amf_collection.insert_one(content)
        importlib.reload(callbacks)
        handle_registered_ue_callbacks()
        handle_changed_status_callbacks()

    return "OK"


# Route for SMF notifications
@app.route('/callbacks/dataplane-reports', methods=['POST'])
def receive_smf_notification():
    if request.method == 'POST':
        content = request.get_json(force=True)
        log.debug(content)
        smf_collection.insert_one(content)

    return "OK"

app.config["DEBUG"] = False
app.run(host='192.168.71.129', port=1112)

# Define termination handler
def terminator(signum, frame, ask=True):
    log.info("Terminating...")

    if amf_sub != "":
        url = amf_sub
        response = requests.delete(url)
        log.info(f"AMF Subscription delete status code: {response.status_code}")

    if smf_sub != "":
        url = smf_sub
        response = requests.delete(url)
        log.info(f"SMF Subscription delete status code: {response.status_code}")

signal.signal(signal.SIGTERM, terminator)
signal.signal(signal.SIGINT, terminator)
signal.pause()
