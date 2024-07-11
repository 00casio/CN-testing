import os
import sys
import logging
import multiprocessing
import time
import yaml
from pymongo import MongoClient
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(parent_dir)
sys.path.insert(0, parent_dir)
time.sleep(10)
from sdk.src.modules.RFsimUEManager import add_ues, remove_ues
from sdk.src.main.init_handler import start_handler, stop_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_imsi_from_docker_yaml(docker_yaml_path):
    with open(docker_yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    imsis = []
    for service_name, config in data['services'].items():
        if service_name.startswith('oai-nr-ue'):
            environment = config.get('environment', [])
            options = environment['USE_ADDITIONAL_OPTIONS']
            parts = options.split()
            if '--uicc0.imsi' in parts:
                imsi_index = parts.index('--uicc0.imsi') + 1
                if imsi_index < len(parts):
                    imsis.append(parts[imsi_index])
    if imsis:
        return imsis
    else:
        logger.error("No IMSIs found in Docker YAML file")
        sys.exit(1)

def get_imsi_from_handler_collection():
    logging.getLogger('pymongo').setLevel(logging.INFO)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['notification_db']
    amf_collection = db['amf_notifications']
    latest_imsi_events = {}
    for document in amf_collection.find():
        for report in document["reportList"]:
            supi = report["supi"]
            rm_state = report["rmInfoList"][0]["rmState"]
            timestamp = report["timeStamp"]
            if supi.startswith("imsi-"):
                supi = supi[5:]
            if supi not in latest_imsi_events or timestamp > latest_imsi_events[supi]['timestamp']:
                latest_imsi_events[supi] = {'rm_state': rm_state, 'timestamp': timestamp}
    latest_registered_imsis = [
        imsi for imsi, event in latest_imsi_events.items()
        if event['rm_state'] == "REGISTERED"]
    return latest_registered_imsis

def check_imsi_match(docker_yaml_path,nb_of_users):
    imsi_from_yaml = extract_imsi_from_docker_yaml(docker_yaml_path)[:nb_of_users]
    imsi_from_handler = get_imsi_from_handler_collection()
    if set(imsi_from_yaml) == set(imsi_from_handler):
        logger.info("IMSI match successful.")
    else:
        logger.error(f"IMSI mismatch. Docker YAML IMSI: {imsi_from_yaml}, Handler IMSI: {imsi_from_handler}")
        remove_ues(nb_of_users)
        stop_handler()
        sys.exit(1)

def add_ues_process():
    try:
        add_ues(1)
        logger.info("UEs were successfully added.")
    except Exception as e:
        logger.error(f"Core network is not healthy. UEs were not added: {e}")
        stop_handler()
        sys.exit(1)

if __name__ == "__main__":
    add_ues_process()
    time.sleep(30)
    remove_ues(1)
    try:
        start_handler()
    except Exception as e:
        logger.error(f"Failed to start handler: {e}")
        sys.exit(1)

    # Give the handler some time to start
    time.sleep(20)
    nb_of_users = 5
    for user in range(nb_of_users):
        try:
            ues_proc = multiprocessing.Process(target=add_ues_process)
            ues_proc.start()
            ues_proc.join()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Failed to add UEs: {e}")
            sys.exit(1)
        
    time.sleep(10)
    docker_yaml_path = os.path.join(parent_dir, '5g_rfsimulator', 'docker-compose.yaml')
    check_imsi_match(docker_yaml_path, nb_of_users)

    time.sleep(3)
    try:
        remove_ues(nb_of_users)
    except Exception as e:
        logger.error(f"Failed to stop handler: {e}")
        sys.exit(1)
    time.sleep(3)
    
    logger.info("Stopping handler...")
    try:
        stop_handler()
    except Exception as e:
        logger.error(f"Failed to stop handler: {e}")
        sys.exit(1)
        
    logger.info("Handler stopped.")
    sys.exit(0)
