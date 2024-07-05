import os
import subprocess
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)
from sdk.src.modules.RFsimUEManager import add_ues
from sdk.src.main.init_handler import start_handler
home_dir = os.path.expanduser("~")
directory = os.path.join(home_dir,'openairinterface5g-develop', 'ci-scripts', 'yaml_files', '5g_rfsimulator')
os.chdir(directory) 
commands = [
    "docker pull mysql:8.0",
    "docker pull oaisoftwarealliance/oai-amf:v2.0.0",
    "docker pull oaisoftwarealliance/oai-smf:v2.0.0",
    "docker pull oaisoftwarealliance/oai-upf:v2.0.0",
    "docker pull oaisoftwarealliance/trf-gen-cn5g:focal",
    "docker pull oaisoftwarealliance/oai-gnb:develop",
    "docker pull oaisoftwarealliance/oai-nr-ue:develop",
    "docker-compose up -d mysql oai-amf oai-smf oai-upf oai-ext-dn"
]
# for command in commands:
#     subprocess.run(command, shell=True)
add_ues(1)

