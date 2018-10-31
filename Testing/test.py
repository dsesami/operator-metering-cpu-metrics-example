from kubernetes import client, config
import datetime
# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()

def get_pod_names(namespace= "openshift-metering"):
    """Returns a list of the names of pods in the namespace"""
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if "openshift-metering" in i.metadata.namespace:
            print(i.metadata.name)

def get_utc_timestamp():
    """Returns the current UTC Time in proper format"""
    d = datetime.datetime.utcnow()
    fmt_str = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z'
    return(fmt_str.format(d.year, d.month, d.day, d.hour, d.minute, d.second))

print("Listing pods with their IPs:")
time = get_utc_timestamp()
print(time)
get_pod_names()    
