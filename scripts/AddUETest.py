import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)
from sdk.src.modules.RFsimUEManager import add_ues
from sdk.src.modules.RFsimUEManager import remove_ues
import subprocess
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    try:
        remove_ues(1)
        # logger.info("UEs added successfully")
    except Exception as e:
        logger.error("Core network is not healthy. UEs were not added.")