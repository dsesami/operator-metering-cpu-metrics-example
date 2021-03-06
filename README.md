# Using Operator Metering for Processing of CPU Metrics

### Disclaimer:
This example assumes you have [Operator Metering](https://github.com/operator-framework/operator-metering) installed and running on an [OpenShift](https://www.openshift.com/) instance. See [this directory](https://github.com/operator-framework/operator-metering/tree/master/Documentation) for significantly more detailed information on the architecture and usage of Operator Metering. 


## Goals

We will create a manual report which collects total CPU-core-seconds used by all pods labled with `com.example.product=demo-product`. CPU core-seconds is defined as:
```
(# of CPU cores) * (% total utilization) * (total time in seconds)
```
So, 2 cores running at 100% utilization for 5 minutes (the same as 300 seconds) would equal: 
```
(2) * (1.00) * (300), or 600 CPU core-seconds.
```

We will also create a scheduled report that lists the hourly peak CPU usage (the total sum of percent total utilization of each core) of a pod, and sorts it from high to low. The report will run each hour. This will also only look for pods labeled with `com.example.product=demo-product.`

[Here is the documentation on how to label pods (or any object) in OpenShift/Kubernetes.](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)

## Background
Operator Metering uses [Prometheus](https://prometheus.io/) to query OpenShift instances for raw data. The data collected will be based on what Prometheus can access. If it can see every project/cluster, then every single pod that is labeled correctly, regardless of its namespace, will appear in the query result.

Operator Metering provides a few custom OpenShift/Kubernetes resources for use. There are several built in instances of these resource types, which provide raw information about CPU and memory usage. For example, you can try `oc get reportgenerationqueries` to see available queries to use in metering reports. Here is a summary of the resource types:
- **ReportPrometheusQuery**: This tells Prometheus which data to search for inside of the OpenShift instance. In the example, this is `kube-pod-label-reportprometheusquery.yaml`, and contains the filter for the resource label. To look for a label, the query is prefixed with `label_` and all periods in the label key (not the value itself) are replaced with underscores.So to search for the resource label `com.example.product="demo-product"`, the filter is `label_com_example_product="demo-product"`.
- **ReportDataSource**: This represents how to store data, and sometimes how to collect the data. In the example `kube-pod-label-demo-reportdatasource.yaml`, the `promsum` key tells Operator Metering to periodically poll Prometheus for the specified metrics in the ReportPrometheusQuery.
- **ReportGenerationQuery**: We have two of these, `demo-cpu-core-seconds-reportgenerationquery.yaml`, and `demo-peak-cpu-usage-reportgenerationquery.yaml`. They contain the SQL statements (with some Go templating) to hit the Presto database where all of the raw data is stored. They also contain information about how columns will be represented. The templating is used by reports to generate beginning and end time frames for the query, and also to reference existing database information provided by other queries or Operator Metering/Prometheus. 
- **Report**: This contains a start and end time for reports, as well as the `runImmediately` flag, which attempts to build the report ignoring the reporting end time or any grace period that the report waits for upon completion. See the Operator Metering documentation for more information about reports.
- **ScheduledReport**: This is similar to a regular report, except it executes on a regular, scheduled basis.

### Summary of Background
A ReportDataSource tells Operator Metering to use a particular ReportPrometheusQuery (to zone in on the labeled pods we want) to capture data using available ReportGenerationQueries (to identify exactly what data we want). Once the ReportGenerationQuery that you want has been running, you can use a Report or a ScheduledReport to generate a report on whatever data you need.

## Creating a Stress Test
If you would like to use some dummy images to demonstrate CPU strain, follow these steps. Note that Operator Metering will only be looking for images with the proper label, and it does not care what the images actually _are_ in this case.

### Creating a Stress Image:
If you do not have a DockerHub account, create one. This will allow you to host images that can be imported into OpenShift. Assign your username to an environment variable called DOCKER_ID_USER. In bash this can be done with `export DOCKER_ID_USER=username`.

1. In your desired directory, `git clone` https://github.com/simon3z/docker-stress-test.git
2. `cd docker-stress-test`
3. Go into the `Dockerfile` and add the line `LABEL com.example.product="demo-product"`
4. To import from DockerHub: `docker login docker.io`
5. `docker build [path to docker stress test dir]/docker-stress-test`
6. Use `docker images` to list out all the available images. Find the stress test image as it is untagged when built with this repo. The image may have a name like c27504b5a55d, which we will use in this example.
7. We can give our image a more readable name, like Stresser A. Here, it is tagged with `docker tag c27504b5a55d docker.io/$DOCKER_ID_USER/stressera`.
8. Push your image to DockerHub: `docker push docker.io/$DOCKER_ID_USER/stressera`
9. Import the image into OpenShift: `oc import-image docker.io/$DOCKER_ID_USER/stressera --confirm`.

### Running stress tests

You can create as many Docker stress test images as you like and import them. 

##### Creating Stress Test instance

If there are no created stress instances, they can be created using `oc run`:

```
oc run --image=docker.io/$DOCKER_ID_USER/stressera stressera
```

##### Get instance name

Next, determine what the running instance is of your stress test with `oc get pods`. It will be of the format `[instance-name]-[deployment-#]-[random-suffic]`, so look for the name. For example, the one created in the previous step shows up as `stresser1-1-cqc79`.

##### Stress an instance

To stress an image, run a command of the following format:

```
oc exec [CONTAINER_NAME] -- stress -c [NUMBER OF CORES] -t [STRESS TIME IN SECONDS] &
```

The `&` will run the process in the background. As such, an example command to stress 2 cores for 120 seconds (2 minutes) might look like:

```
oc exec stresser1-1-cqc79 -- stress -c 2 -t 120 &
```

You should make note of the time the stress test started, in UTC time. On many systems this can be done by running the `date` command.
To get the start time in a format we can use in reports, we can run:

```
date --utc +%FT%TZ
```

To get an exact start time, you can chain the commands:

```
date --utc +%FT%TZ; oc exec stresser1-1-cqc79 # and so forth.
```

## Workflow for Creating a Manual Report
Assuming you have the YAML files provided with this directory, and you have an OpenShift instance running with pods that have been labeled `com.example.product=demo-product`. 

**NOTE**: If you want to use a different key/value for your label, you need to edit the ReportPrometheusQuery to use your desired label key and value. Ensure that the key is all underscores -- use this example as a model. In addition, you need to change the key name in all SQL queries provided in the ReportGenerationQueries. 

If you want to change the name of your resources and reports, you need to change the `metadata.name` value in the file. Bear in mind you need to change the name in any other files where that name is referenced.

To create a report that measures CPU-core-seconds utilized for a given time frame:
```
oc create -f kube-pod-label-demo-reportprometheusquery.yaml
oc create -f kube-pod-label-demo-reportdatasource.yaml
oc create -f demo-cpu-core-seconds-reportgenerationquery.yaml
```
Data collection will then accumulate. To create a manual report, open the `demo-cpu-core-seconds-report.yaml` file and edit the `reportingStart` and `reportingEnd` times. **Note that these times need to be in UTC time, and that the report will output timestamps in UTC.** If the `runImmediately` flag is set to false, a default 5 minute grace period will occur after the `reportingEnd` time. With this example query, the data is complex enough that you may have to give it 10+ minutes after
reporting resolves for the query to have even populated the data -- you may successfully run the report and only have gotten blank data. If this happens, delete the report and create a new one a while later, and the fields should populate with the new report. As such, it is currently advisable to run a report start/end time that has already passed some time ago. 

To create the report:
```
oc create -f demo-cpu-core-seconds-report.yaml
# Wait for the report to complete. To view status, simply run:
oc get report demo-cpu-core-seconds-usage -o yaml  # or json, or whatever is available
```
You can access the results of the report locally. To do so, run `oc proxy` in another terminal to make the API available on port 8001. Then, in your original terminal, run:
```
curl "http://127.0.0.1:8001/api/v1/namespaces/YOUR_NAMESPACE_HERE/services/https:reporting-operator:http/proxy/api/v1/reports/get?name=demo-cpu-core-seconds-usage&format=tabular"
```
A few notes about this call: 
- Edit the namespace to whichever project Operator Metering is currently residing.
- If you're getting some kind of security error, try changing the `https` right before `reporting-operator` to plain `http`.
- The name `demo-cpu-core-seconds-usage` can be changed to what your report is named.
- The `api/v1/reports/get` section can be changed to `api/v1/scheduledreports/get` if you're running a ScheduledReport instead.
- The `format` option at the end of the call can also be `yaml` or `json`.

## Workflow for Creating a Scheduled Report
This is extremely similar to the normal report. If you haven't already created them, run:
```
oc create -f kube-pod-label-demo-reportprometheusquery.yaml
oc create -f kube-pod-label-demo-reportdatasource.yaml
```
Then, create the ReportGenerationQuery that checks for peak CPU usage:
```
oc create -f demo-peak-cpu-usage-reportgenerationquery.yaml
```
Create the scheduled report so it starts accumulating the data into the report on the hour:
```
oc create -f demo-peak-cpu-usage-scheduledreport.yaml
```
Wait some time for hourly reports to accumulate, then use `oc proxy` and `curl` as detailed in the section on manual reports, with the adjustments in the notes.

## Automation (in progress)
This workflow can be automated to an extent. If you have created everything minus the Report/ScheduledReport objects, you can use stresstest.sh to perform a container stress test. The shell script will automatically build a report YAML file that runs for the duration of the stress test.
