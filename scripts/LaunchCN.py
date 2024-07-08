import os
import subprocess
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a function to execute shell commands with error checking
def run_command(command):
    logger.info(f"Running command: {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        logger.error(f"Command failed with error: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command)
    else:
        logger.info(f"Command succeeded: {result.stdout}")

# Set up paths
try:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, parent_dir)

    home_dir = os.path.expanduser("~")
    directory = os.path.join(home_dir, 'openairinterface5g-develop', 'ci-scripts', 'yaml_files', '5g_rfsimulator')
    os.chdir(directory)
except Exception as e:
    logger.error(f"Error setting up paths or importing modules: {e}")
    raise

# Construct the path to handler.py
handler_dir = os.path.abspath(os.path.join(parent_dir, 'sdk/src/main'))
handler_path = os.path.join(handler_dir, 'handler.py')

# List of docker commands
commands = [
    "docker pull mysql:8.0",
    "docker pull oaisoftwarealliance/oai-amf:v2.0.0",
    "docker pull oaisoftwarealliance/oai-smf:v2.0.0",
    "docker pull oaisoftwarealliance/oai-upf:v2.0.0",
    "docker pull oaisoftwarealliance/trf-gen-cn5g:focal",
    "docker pull oaisoftwarealliance/oai-gnb:develop",
    "docker pull oaisoftwarealliance/oai-nr-ue:develop",
    "docker-compose up -d mysql oai-amf oai-smf oai-upf oai-ext-dn",
]

# Run each command and check for errors
try:
    for command in commands:
        run_command(command)
except subprocess.CalledProcessError as e:
    logger.error(f"Deployment command failed: {e}")
    raise

logger.info("All commands executed successfully.")
