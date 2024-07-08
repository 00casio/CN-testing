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

try:
    # Get the parent directory of the current script file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate two folders back to reach the desired directory
    directory = os.path.abspath(os.path.join(current_dir, '..','5g_rfsimulator'))
    parentdir= os.path.abspath(os.path.join(current_dir, '..','..'))
    
    # Change the current working directory to the desired directory
    os.chdir(directory)
    logger.info(f"Changed current working directory to: {directory}")
    
except Exception as e:
    logger.error(f"Error setting up paths or importing modules: {e}")
    raise

# Construct the path to handler.py
# handler_dir = os.path.abspath(os.path.join(parentdir, 'sdk/src/main'))
# handler_path = os.path.join(handler_dir, 'handler.py')

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
