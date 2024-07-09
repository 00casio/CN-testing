import os
import sys
import logging
import multiprocessing
import time
import yaml
from pymongo import MongoClient

# Set up paths
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Import necessary functions from the sdk
from sdk.src.modules.RFsimUEManager import add_ues, remove_ues
from sdk.src.main.init_handler import start_handler, stop_handler

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Placeholder function to extract IMSI from Docker YAML file
# def extract_imsi_from_docker_yaml(docker_yaml_path):
#     with open(docker_yaml_path, 'r') as file:
#         data = yaml.safe_load(file)
    
#     imsis = []
#     for service_name, config in data['services'].items():
#         if service_name.startswith('oai-nr-ue'):
#             environment = config.get('environment', [])
#             options = environment['USE_ADDITIONAL_OPTIONS']
#             parts = options.split()
#             if '--uicc0.imsi' in parts:
#                 imsi_index = parts.index('--uicc0.imsi') + 1
#                 if imsi_index < len(parts):
#                     imsis.append(parts[imsi_index])
    
#     if imsis:
#         return imsis
#     else:
#         raise ValueError("No IMSIs found in Docker YAML file")

# # Function to get IMSI from the handler's MongoDB collection
# def get_imsi_from_handler_collection():
#         ##get it from the handler database
#         # return it
#     return None

# # Function to check if the handler's IMSI matches the IMSI from the Docker YAML
# def check_imsi_match(docker_yaml_path):
#     imsi_from_yaml = extract_imsi_from_docker_yaml(docker_yaml_path)
#     imsi_from_handler = get_imsi_from_handler_collection()
    
#     if imsi_from_yaml == imsi_from_handler:
#         logger.info("IMSI match successful.")
#     else:
#         logger.error(f"IMSI mismatch. Docker YAML IMSI: {imsi_from_yaml}, Handler IMSI: {imsi_from_handler}")

# def add_ues_process():
#     try:
#         add_ues(1)
#         logger.info("UEs were successfully added.")
#     except Exception as e:
#         logger.error(f"Core network is not healthy. UEs were not added: {e}")

# if __name__ == "__main__":
#     # Start the handler in the main process
#     try:
#         start_handler()
#     except Exception as e:
#         logger.error(f"Failed to start handler: {e}")
#         sys.exit(1)
    
#     # Give the handler time to start
#     time.sleep(10)
    
#     # Start the add_ues function in a separate process
#     ues_proc = multiprocessing.Process(target=add_ues_process)
#     ues_proc.start()

#     # Wait for the add_ues process to finish
#     ues_proc.join()

#     # Check IMSI match
#     docker_yaml_path = os.path.join(parent_dir, '5g_rfsimulator', 'docker-compose.yaml') # Change this path to the correct Docker YAML path depending on the image working on 
#     check_imsi_match(docker_yaml_path)
    
#     # Keep the handler running (remove this line if you want the script to exit)
#     time.sleep(10)
    
#     logger.info("Stopping handler...")
#     remove_ues(1)
#     stop_handler()
#     logger.info("Handler stopped.")
#     sys.exit(0)

add_ues(1)
