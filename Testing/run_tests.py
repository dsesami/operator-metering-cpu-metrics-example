"""Functions to call oc commands"""

import subprocess
import datetime
import re
import yaml
#import random
#import sys

## Helper Functions
def run_cmd(cmd):
    """Run a system command"""
    result = subprocess.run(cmd.split(" "),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result


def get_utc_timestamp(fmt_str='{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z'):
    """Returns the current UTC Time in proper format"""
    date = datetime.datetime.utcnow()
    formatted_date = fmt_str.format(date.year,
                                    date.month,
                                    date.day,
                                    date.hour,
                                    date.minute,
                                    date.second)
    return formatted_date

def get_pod_names(pod_subname, namespace='default'):
    """Returns the full container pod names from sub-name"""
    print(pod_subname, namespace)
    regex = re.compile(pod_subname + r'-\d+-.{5}')
    result = run_cmd("oc get pods -n {!s}".format(namespace))
    match_names = regex.findall(str(result.stdout))
    return match_names

## Test Spec functions
def load_test_spec(spec_src):
    """Loads the test spec"""
    with open(spec_src, 'r') as spec_file:
        spec = yaml.load(spec_file)
    return spec


## Test Procedure Functions
def run_all_test_cases():
    """Loops over the defined test cases"""


def run_test_case():
    """Runs the generic test case, based on test spec"""
    ## Record Time

    ## Run OC Steps

    ## Generate Report

    ## Check Test Case

def record_time():
    """Records the time at the start of the test case"""


def run_oc_steps():
    """Runs the 'oc' steps of the test case"""
    ## New Project Step

    ## Run Steps

    ## Scale Steps

    ## Exec Steps

def run_procedure(test_spec, run_key="run"):
    """Runs the run operations"""
    run_spec = test_spec[run_key]
    for run in run_spec:
        args = run_spec[run]
        arg_str = args + " " if args else ''
        cmd = "oc run {!s}{!s}".format(arg_str, run)
        print(cmd)

def exec_procedure(test_spec, exec_key="exec"):
    """Runs the exec case"""
    exec_spec = test_spec[exec_key]
    for exec_call in exec_spec:
        print(exec_call)


def generate_report():
    """Generates the operator-metering report"""


def run_check_case():
    """checks if the test case passed/failed"""
