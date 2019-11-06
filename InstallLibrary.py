###################################################################
#  Script to install libraries on cluster
#  1) install library using Databricks rest api ( install is asyncronous)
#  2) monitor the package status polling the status
#     - in status is INSTALLED   -> success
#     - if status is FAILED      -> failure  
#     - if status is INSTALLING  -> wait for 10 seconds and iterate 
#     - if package not found     -> failure
###################################################################

import requests
import base64
import time
import sys


# install library using databricks rest api (install is asyncronous)
# > tokenb: Databricks personal token (utf-8)
# > domain: Databricks domain
# > clusterId: ID of the cluster previously created
#
# < libraries: path of the file containing the list of libraries
def installLibraries(tokenb, domain, clusterId, libraries):
  response = requests.post(
    domain + '/api/2.0/libraries/install',
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)},

    json={
    "cluster_id": clusterId,
    "libraries": getLibrariesFromFile(libraries)
    }
  )

  if (response.status_code == 200):
    print('Installing following packages: ' , getLibrariesFromFile(libraries))
  else:
    print("Error installing packages: %s: %s" % (response.json()["error_code"], response.json()["message"]))
  return

# get libraries from txt file (both Maven and PyPi)
# > libraries_file: path of the file containing the list of libraries
#
# < libs: list of libraries to be installed
def getLibrariesFromFile(libraries_file):
  with open(libraries_file) as fp:
    content = fp.readlines()
  content = [x.strip() for x in content]

  libs = []
  for item in content:
    if "maven" in item:
      coords = {}
      coords["coordinates"] = item.rpartition(' - ')[2]
      dic = {}
      dic["maven"] = coords
      libs.append(dic)
    elif "pypi" in item:
      pak = {}
      pak["package"] = item.rpartition(' - ')[2]
      dic = {}
      dic["pypi"] = pak
      libs.append(dic)
    else:
      print("Error: specify either 'maven' or 'pypi'")
  return libs

# get info about packages using Databricks API
# > tokenb: Databricks personal token (utf-8)
# > domain: Databricks domain
# > clusterId: ID of the cluster previously created
def getPackageInstallationStatus(tokenb, domain, clusterId):
  response = requests.get(
    domain + '/api/2.0/libraries/cluster-status?cluster_id=' + clusterId,
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)}
  )

  found = False
  while(1):
    for e in response.json()['library_statuses']:
      if 'pypi' in e['library']:
        pyp = e['library']['pypi']
        if pyp != "":
          package= e['library']['pypi']['package']
          found=True
      elif 'maven' in e['library']:
        pyp = e['library']['maven']
        if pyp != "":
          package= e['library']['maven']['coordinates']
          found=True
      else:
        print('No accepted packages found')
      if found:
        status = e['status']
        print('Package: ', package)
            
        if (status=="INSTALLED"):
          print(status)
          continue
        if (status=="FAILED"):
          print(status +': '+ e['messages'][0])
          continue
          
        if (status=="INSTALLING" or status=="RESOLVING"):
          print(status)
          time.sleep(10)
          response = requests.get(
              domain + '/api/2.0/libraries/cluster-status?cluster_id=' + clusterId,
              headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)}
          )
    return

# DEPRECATED - get info about packages using Databricks API
def getPackageInstallationStatusPyPi(tokenb, domain, clusterId):
  # get packages installation status of the input cluster id 
  response = requests.get(
    domain + '/api/2.0/libraries/cluster-status?cluster_id=' + clusterId,
    headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)}
  )  

  # monitor input package instalaltion status :
  #     - in status is INSTALLED   -> success
  #     - if status is FAILED      -> failure  
  #     - if status is INSTALLING  -> wait for 10 seconds and iterate 
  #     - if package not found     -> failure

  while(1):
    for e in response.json()['library_statuses']:
      pyp = e['library']['pypi']
      status = e['status']
      if pyp != "":
        package= e['library']['pypi']['package']
        print('Package: ', package)  
        
        if (status=="INSTALLED"):
          print(status)
          continue
        
        if (status=="FAILED"):
          print(status +': '+ e['messages'][0])
          continue
          
        while (status=="INSTALLING"):
          print(status)
          time.sleep(10)
          response = requests.get(
              domain + '/api/2.0/libraries/cluster-status?cluster_id=' + clusterId,
              headers={'Authorization': b"Basic " + base64.standard_b64encode(b"token:" + tokenb)}
          )
          print(response.json())
    return

# DEPRECATED - get libraries names (from Maven) from txt and put in json structure to feed Databricks API
def getLibrariesFromFileMaven():
  with open('libraries.txt') as fp:
    content = fp.readlines()
  content = [x.strip() for x in content]

  libs = []
  for item in content:
    coords = {}
    coords["coordinates"] = item
    dic = {}
    dic["maven"] = coords
    libs.append(dic)

  return libs

# DEPRECATED -  get libraries names (from PyPi) from txt and put in json structure to feed Databricks API
def getLibrariesFromFilePyPi():
  with open('libraries_pypi.txt') as fp:
    content = fp.readlines()
  content = [x.strip() for x in content]

  libs = []
  for item in content:
    pak = {}
    pak["package"] = item
    dic = {}
    dic["pypi"] = pak
    libs.append(dic)
  return libs