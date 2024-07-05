import sys
import os
import requests
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)
import yaml
from utils import load_config



def modifyAmfSubscription(amf_ip, amf_port, subscription_id,amf_url='/namf-evts/v1',new_nfid=None,new_notify_uri=None):
    url = f"http://{amf_ip}:{amf_port}{amf_url}/subscriptions/{subscription_id}"
    sub_body = {
    "op": "remove",
    "path": "/options/expiry",
    "value": "2024-07-13T08:30:00Z"
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

def deleteAmfSubscription(amf_ip, amf_port, subscription_id,amf_url='/namf-evts/v1'):
    url = f"http://{amf_ip}:{amf_port}{amf_url}/subscriptions/{subscription_id}"
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
configs = load_config("configs.yaml")
print(modifyAmfSubscription(amf_ip = configs["amf"]["ip"],amf_port = configs["amf"]["port"],subscription_id='1'))