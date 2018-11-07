"""Some functions to help with automated testing"""

import time
import datetime
from pprint import pprint
import openshift
import kubernetes



## Openshift OC-like functions

def init():
    """Initialize connection to kubernetes"""
    kubernetes.config.load_kube_config()
    conn = kubernetes.client.CoreV1Api()
    return conn

def create_api_client_instance():
    """Creates and returns an API instance to use"""
    configuration = openshift.client.Configuration()
    ## Need to add API key stuff here????
    ## Or Tokens???
    api_instance = openshift.client.ProjectOpenshiftIoV1Api(
        openshift.client.ApiClient(configuration)
    )
    return api_instance

def create_core_api_instance():
    """Creates core api instance"""
    ### Too many of these functions. I'll have to figure out what they
    ### actually are and clean them up then...
    kubernetes.config.load_kube_config()
    conf = kubernetes.client.Configuration()
    conf.assert_hostname = False
    kubernetes.client.Configuration.set_default(conf)
    api = kubernetes.client.CoreV1Api()
    return api


def get_pod_names(conn, namespace="openshift-metering"):
    """Returns a list of the names of pods in the namespace"""
    ret = conn.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if namespace in i.metadata.namespace:
            print(i.metadata.name)


def new_project(api_instance, project_name, pretty="pretty"):
    """Creates a new openshift project (like oc new-project)"""
    body = openshift.client.V1Project()
    body.metadata = kubernetes.client.V1ObjectMeta(name=project_name)
    try:
        api_response = api_instance.create_project(body, pretty=pretty)
        pprint(api_response)
    except kubernetes.client.rest.ApiException as api_exception:
        print("Exception when calling ProjectOpenshiftIoV1Api->create_project: %s\n"
              % api_exception)


def delete_project(api_instance, project_name, pretty="pretty"):
    """Deletes an openshift project"""
    try:
        api_response = api_instance.delete_project(project_name, pretty=pretty)
        pprint(api_response)
    except kubernetes.client.rest.ApiException as api_exception:
        print("Exception when calling ProjectOpenshiftIoV1Api->delete_project: %s\n"
              % api_exception)


def get_projects():
    """Returns a list of the projects"""


def create_pod_manifest(name, image, args):
    """Creates and returns a pod_manifest for create_pod()"""
    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': name
        },
        'spec': {
            'containers': [{
                'image': image,
                'name': 'sleep',
                "args": args
            }]
        }
    }
    return pod_manifest


def create_pod(api, name, image, args, namespace='default'):
    """Create a new pod"""
    pod_manifest = create_pod_manifest(name, image, args)
    resp = api.create_namespaced_pod(body=pod_manifest,
                                     namespace=namespace)
    while True:
        resp = api.read_namespaced_pod(name=name,
                                       namespace=namespace)
        if resp.status.phase != 'Pending':
            break
        time.sleep(1)
    print("Done.")
    return resp

def exec_pod(api, name, exec_command, namespace=None):
    """executes a pod"""
    response_message = kubernetes.stream.stream(api.connect_get_namespaced_pod_exec,
                                                name, namespace,
                                                command=exec_command,
                                                stderr=True, stdin=True,
                                                stdout=True, tty=False)
    return response_message

def get_containers(conn, namespace=None):
    """Returns a list of contaienr names"""
    ret = conn.list_pod_for_all_namespaces(watch=False)
    container_names = []
    for container_info in ret.items:
        in_namespace = namespace and container_info.metadata.namespace in namespace
        if not namespace or in_namespace:
            container_names.append(container_info.metadata.name)
    return container_names


def get_container_matches(conn, match_string, namespace=None):
    """Returns a list of containers with a matched name"""
    all_container_list = get_containers(conn, namespace=namespace)
    match_list = list(filter
                      (lambda container_name:
                       match_string in container_name, all_container_list))
    return match_list


def scale_deployment():
    """Scales a deployment (like oc scale)"""


## Testing Helper Functions
def get_utc_timestamp():
    """Returns the current UTC Time in proper format"""
    date = datetime.datetime.utcnow()
    fmt_str = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z'
    return fmt_str.format(date.year, date.month, date.day, date.hour, date.minute, date.second)
