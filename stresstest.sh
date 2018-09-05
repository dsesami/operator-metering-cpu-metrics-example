#!/bin/bash

usage() {
    echo "usage: (all are mandatory)
    -c CONTAINER_NAME
    -g GENERATIONQUERY
    -n NUMBER_OF_CORES
    -o OUTPUT_FILENAME (without suffix)
    -r REPORT_NAME
    -t TOTAL_RUN_TIME (in seconds)"
}

stress() {
    oc exec $CONTAINER_NAME -- stress \
        -c $NUMBER_OF_CORES \
        -t $TOTAL_RUN_TIME &
}

CONTAINER_NAME=""
GENERATIONQUERY=""
NUMBER_OF_CORES=""
OUTPUT_FILENAME=""
REPORT_NAME=""
TOTAL_RUN_TIME=""

while getopts c:n:o:r:t: arg
do
    case $arg in
        c)
            CONTAINER_NAME=$OPTARG;;
        n)
            NUMBER_OF_CORES=$OPTARG;;
        o)
            OUTPUT_FILENAME=$OPTARG;;
        r)
            REPORT_NAME=$OPTARG;;
        t)
            TOTAL_RUN_TIME=$OPTARG;;
    esac
done

if  [ -z $CONTAINER_NAME ]  || \
    [ -z $GENERATIONQUERY ] || \
    [ -z $NUMBER_OF_CORES ] || \
    [ -z $OUTPUT_FILENAME ] || \
    [ -z $REPORT_NAME ] || \
    [ -z $TOTAL_RUN_TIME ]
then
    usage
    exit 1
fi

stress
START_TIME=$(date --utc +%FT%TZ)
END_TIME=$(date --utc --date="+ $TOTAL_RUN_TIME seconds" +%FT%TZ)
sed -e "s/START_TIME/${START_TIME}/" \
    -e "s/END_TIME/${END_TIME}/" \
    -e "s/CORE_SECONDS_REPORT_NAME/${REPORT_NAME}/" \
    -e "s/GENERATIONQUERY/${GENERATIONQUERY}/" \
    <core-seconds-report-template.yaml >$OUTPUT_FILENAME.yaml
echo "Stress test started for $TOTAL_RUN_TIME seconds on container $CONTAINER_NAME."
echo "............................................................................."
echo "A report named $OUTPUT_FILENAME.yaml has been created."
echo "The reportgenerationquery $GENERATIONQUERY was used."
echo "The report will run from $START_TIME to $END_TIME"
echo "............................................................................."
echo "When the stress test is complete, you may create the report by running:

     'oc create -f $OUTPUT_FILENAME.yaml'

Bear in mind that report data aggregation may take some time after the stress test
is complete. You should wait to run 'oc create' until
several minutes after the stress test is complete."
