"""Some functions to help with automated testing"""

import datetime
import kubernetes

## Openshift OC-like functions

def init():
    """Initialize connection to kubernetes"""
    kubernetes.config.load_kube_config()
    conn = kubernetes.client.CoreV1Api()
    return conn

def get_pod_names(conn, namespace="openshift-metering"):
    """Returns a list of the names of pods in the namespace"""
    ret = conn.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if namespace in i.metadata.namespace:
            print(i.metadata.name)

def new_project():
    """Creates a new openshift project (like oc new-project)"""

def run_container():
    """Runs a container (like oc run)"""

def exec_container():
    """Executes a command in a container (like oc exec)"""

def scale_deployment():
    """Scales a deployment (like oc scale)"""


## Testing Helper Functions
def get_utc_timestamp():
    """Returns the current UTC Time in proper format"""
    date = datetime.datetime.utcnow()
    fmt_str = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z'
    return fmt_str.format(date.year, date.month, date.day, date.hour, date.minute, date.second)

## Testing Wrapepr Functions

print("Listing pods with their IPs:")
get_pod_names(init())
