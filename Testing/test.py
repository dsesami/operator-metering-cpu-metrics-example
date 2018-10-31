"""Some functions to help with automated testing"""

import datetime
import kubernetes

# Configs can be set in Configuration class directly or using helper utility

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

def get_utc_timestamp():
    """Returns the current UTC Time in proper format"""
    date = datetime.datetime.utcnow()
    fmt_str = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z'
    return fmt_str.format(date.year, date.month, date.day, date.hour, date.minute, date.second)

print("Listing pods with their IPs:")
get_pod_names(init())
