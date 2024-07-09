import sys
import os
import requests
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
import yaml
from utils import load_config

def modifySMFSubscription(smf_ip, smf_port, subscription_id,smf_url='/nsmf-evts/v1',new_nfid=None,new_notify_uri=None):
    url = f"http://{smf_ip}:{smf_port}{smf_url}/subscriptions/{subscription_id}"
    sub_body = {
    "op": "add",
    "path": "/eventlist/0",
    "value": "UE_MOBILITY"
  }
    try:
        r = requests.patch(url=url, json=sub_body)
        if r.status_code == 200:
            return r.json()
        elif r.status_code in [307, 308]:
            return {"redirect": r.headers['Location']}
        else:
            return {"error": r.status_code, "message": r.json()}
    except Exception as e:
        return {"error": "exception", "message": str(e)}

def deleteSMFSubscription(smf_ip, smf_port, subscription_id,smf_url='/nsmf-evts/v1'):
    url = f"http://{smf_ip}:{smf_port}{smf_url}/subscriptions/{subscription_id}"
    try:
        r = requests.delete(url=url)
        if r.status_code == 204:
            print(r.status_code)
            return {"status": "Subscription deleted successfully"}
        elif r.status_code in [307, 308]:
            return {"redirect": r.headers['Location']}
        else:
            return {"error": r.status_code, "message": r.json()}
    except Exception as e:
        return {"error": "exception", "message": str(e)}
configs = load_config("/home/foreur/Documents/Hamza_stage/CN-Testing/configs/configs.yaml")
# print(modifysmfSubscription(smf_ip = configs["smf"]["ip"],smf_port = configs["smf"]["port"],subscription_id='2'))