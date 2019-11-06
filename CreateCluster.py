###################################################################
#  Script to create a Databricks cluster
#  1) create a cluster using Databrick rest api  ( asyncronous )
#  2) monitor the progress polling the status
###################################################################

import requests
import base64
import os
import time
import sys

# create the cluster
# > tokenb: Databricks personal token (utf-8)
# > domain: Databricks domain
#
# < clusterId: ID of the cluster
def createCluster(tokenb, domain):

  # create cluster using Databricks API
  response = requests.post(
    '%s/api/2.0/clusters/create' % (domain),
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)},

    json={
          "num_workers":1,
          "cluster_name": "demo-cluster",
          "spark_version": "5.5.x-gpu-scala2.11",
          "node_type_id": "Standard_DS3_v2",
          "autotermination_minutes": 15,
          'spark_env_vars': {
              'PYSPARK_PYTHON': '/databricks/python3/bin/python3',
          }
      }
  )
  clusterid=''

  print('Response status code: ', response.status_code)
  if response.status_code == 200:
    print('Cluster ID: ', response.json()['cluster_id'])
    clusterid =response.json()['cluster_id'] 
  else:
    print("Error launching cluster: %s: %s" % (response.json()["error_code"], response.json()["message"]))
    exit(1)

  # check status of cluster creation
  while (1) :
    response = requests.get(
      domain + '/api/2.0/clusters/get?cluster_id=' +clusterid,
      headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)},
    )

    print(response.json()['state'])
    if (response.json()['state'] == 'RUNNING'):
      break
    elif(response.json()['state'] == 'TERMINATED'):
      print("Error initializing cluster: %s" % (response.json()["state_message"]))
      exit(0)
    time.sleep(60)

  return clusterid

