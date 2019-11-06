###################################################################
#  Script to create a training job
#   - import files from local directory
#   - create a job and attach a notebook
#   - run the job
###################################################################


import requests
import base64
import os
import time
import sys
from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.sdk.api_client import ApiClient

# import directory from local storage into Databricks workspace
# > source_path: path of the source directory in local storage
# > target_path: path of the destination directory in Databricks workspace
# > domain: Databricks domain
# > token: Databricks personal token
def importDirFromLocal(source_path, target_path, domain, token):
  client = ApiClient(
      host = domain,
      token = token
    )
  workspace_api = WorkspaceApi(client)
  workspace_api.import_workspace_dir(
    source_path = source_path,
    target_path = target_path,
    overwrite = True,
    exclude_hidden_files = True
  )
  return

# create job with associated notebook running on a existing cluster
# > tokenb: Databricks personal token (utf-8)
# > domain: Databricks domain
# > clusterId: ID of the cluster previously created
# > notebook: path of the notebook to be attached to the job
#
# < trainingjobid: the ID of the created job
def createStreamingJob(tokenb, domain, clusterId, notebook):

  # create job
  response = requests.post(
    '%s/api/2.0/jobs/create' % (domain),
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)},

    json={
          "name": "Spark Streaming Job",

          "existing_cluster_id": clusterId, 
          "email_notifications": {
              "on_start": [],
              "on_success": [],
              "on_failure": []
          },
          "timeout_seconds": 3600,
          "max_retries": 1,
          "notebook_task": {
              "notebook_path": notebook,
              "base_parameters": []
           }
      }
  )

  trainingjobid=''

  if response.status_code == 200:
    print('Job ID: ' , response.json()['job_id'])
    trainingjobid =response.json()['job_id']
    #exit(0)
  else:
    print("Error creating the training job: %s: %s" % (response.json()["error_code"], response.json()["message"]))
    exit(1)

  # run job
  resp = requests.post(
    '%s/api/2.0/jobs/run-now' % (domain),
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)},

    json={
        "job_id": trainingjobid,
        "notebook_params": {
            "dry-run": "true",
            "oldest-time-to-consider": "1457570074236"
        }
    }
  )

  if resp.status_code == 200:
      print('Run ID: ' , resp.json()['run_id'])
  else:
    print("Error running the training job: %s: %s" % (resp.json()["error_code"], resp.json()["message"]))
  
  return trainingjobid

