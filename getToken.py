from adal import AuthenticationContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
import time
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# these are pre defined costants
authority_host_url = "https://login.microsoftonline.com/"
databricks_resource_id = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
# these are user dependent
user_parameters = {
                    "tenant": "a36de44b-5282-471e-a183-0525987995e9",
                    "clientId": "93b1b19e-4c17-4186-9a07-88561ff3a5dd",
                    "redirect_uri": "http://localhost"
}

TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?'+
'response_type=code&client_id={}&'+
'state={}&resource={}')
# the auth_state can be a random number or can encoded some info
# about the user. It is used for preventing cross-site request
# forgery attacks [ MS_doc ]
auth_state = 12345
# build the URL to request the authorization code
authorization_url = TEMPLATE_AUTHZ_URL.format(
user_parameters['tenant'],
user_parameters['clientId'],
auth_state,
databricks_resource_id)

'''
https://login.microsoftonline.com/a36de44b-5282-471e-a183-0525987995e9/oauth2/authorize?
client_id=93b1b19e-4c17-4186-9a07-88561ff3a5dd
&response_type=code
&redirect_uri=https%3A%2F%2Flocalhost
&response_mode=query
&resource=2ff814a6-3304-4ab8-85cb-cd0e6f879c1d
&state=1234
'''

mail = 'luisa.folla@absontheweb.onmicrosoft.com'
pw = 'Luisa1974'

def get_token_second_way():
    authority_host_url = "https://login.microsoftonline.com/"
    # the Application ID of AzureDatabricks
    databricks_resource_id = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
    # Required user input
    user_parameters = {
        "tenant" : "a36de44b-5282-471e-a183-0525987995e9",
        "clientId" : "93b1b19e-4c17-4186-9a07-88561ff3a5dd",
        "username" : "luisa.folla@absontheweb.onmicrosoft.com",
        "password" : "Luisa1974"
    }
    # configure AuthenticationContext (reference link)
    # authority URL and tenant ID are used
    authority_url = authority_host_url + user_parameters['tenant']
    context = AuthenticationContext(authority_url)
    # API call to get the token (function link)
    token_response = context.acquire_token_with_username_password(
    databricks_resource_id,
    user_parameters['username'],
    user_parameters['password'],
    user_parameters['clientId'])
    # both refresh token and access token will be returned in the
    # token_response as keys ‘refreshToken’ and ‘accessToken’
    refresh_token = token_response['refreshToken']
    access_token = token_response['accessToken']

    return access_token

def get_authorization_code():
    # open a browser, here assume we use Chrome

    # cap = DesiredCapabilities().FIREFOX
    # cap["marionette"] = False
    # C:\Users\higla\Desktop\geckodriver
    # C:\Program Files\Mozilla Firefox
    # capabilities=cap, executable_path="C:\\Users\\higla\\Desktop\\geckodriver.exe"
    try:
        #dr = webdriver.Firefox()
        dr = webdriver.Firefox(executable_path=r'C:\\Users\ABS_PC\Desktop\\gecko\\geckodriver.exe')
        # load the user login page
        dr.get(authorization_url)
        # todo: put info automatically
        dr.find_element_by_name("loginfmt").send_keys("luisa.folla@absontheweb.onmicrosoft.com")
        dr.find_element_by_id("idSIButton9").click()
        time.sleep(1)
        dr.find_element_by_id("i0118").send_keys("Luisa1974")
        dr.find_element_by_id("idSIButton9").click()
        time.sleep(1)
        dr.find_element_by_id("idBtn_Back").click()
        time.sleep(1)
    except Exception as e:
        print(e)
    # dr.find_elements_by_xpath(By.XPATH("//input[@value='Next']")).click()
    # wait until the user login or kill the process
    code_received = False
    code = ''
    while not code_received:
        cur_url = dr.current_url
        if cur_url.startswith(user_parameters['redirect_uri']):
            parsed = urlparse(cur_url)
            query = parse_qs(parsed.query)
            code = query['code'][0]
            state = query['state'][0]
            # throw exception if the state does not match
            if state != str(auth_state):
                raise ValueError('state does not match')
            code_received = True
            print(code)
            dr.close()
    if not code_received:
        print('Error in requesting authorization code')
        dr.close()
    # authorization code is returned. If not successful,
    # then an empty code is returned
    return code


code = 'AQABAAIAAACQN9QBRU3jT6bcBQLZNUj73IVyHect2o4ZwhhML0keJ2T4QR_AqbPIsw4xCM4xbcIjrUiWghpHKd9rnzkiPJFc3GE4ThEiyHCtq3-zAH8gZvMffx1xhjhXJAiyikAhNf7uD1QufHzPgwOJYldVu2GNToIiCkxgD79If9cW6dQF_BHUke2OBWlxTL47PM_lJbh0QOiS-78O39h9eQqlJrcegn3qUqXePpfbaDrvOgglxoOFI8xlsW0JrzuZX8aMxO4LEJqPlhMbJ9sUTUL_YRMKYyEtg7wUvLAIphtyB02oHqAsvEJ9oY0J4DTcVJYZP-4a9_TYRuHyywuO5ppBUEqNVBpRGk_2prGZT6KsnhifcYnOdVb14-ub1KSKzOIdxvbNNqfttLsnXL97BxijCBmVXrLIrZMpdz43ZWezcE8zIOaHbjyq8mQZdzd1nv1SbdpEKAgbwwUedrmDtlnVJXAwl4hmXp3sAJLh2WJPXqh1ZAW7JsmpykvNbyxUd95bNtIRAiP2xBOD7HF9ttp4sGJftiB7iz5kC4VGf-At_w7XtZLcqKh63kfSU_XEiBoKeCiTD0fTZ49qS9b5XCc4pTEOIAA&state=1234&session_state=c6d7f500-65f9-41be-8e84-6b9179dd5e49'

def get_refresh_and_access_token():
    # configure AuthenticationContext ( reference link )
    # authority URL and tenant ID are used
    authority_url = authority_host_url + user_parameters['tenant']
    context = AuthenticationContext(authority_url)
    # Obtain the authorization code in by a HTTP request in the browser
    # then copy it here
    # Or, call the function ab
    # ove to get the authorization code
    #authz_code = get_authorization_code()
    #authz_code = get_authorization_code_2()
    #authz_code = 'AQABAAIAAACQN9QBRU3jT6bcBQLZNUj7QFYvegwI2NsXUQDA79b66j3drqzcReVttIOzSL_qpnp8kDBkmw0PB-hUSpY-fFeo6pje0ZztlHTdIWESuoEU76Mons8Vvg3BzAN7SQEbS15lpnglf2uBKYL7mpnWleORhcrFFA6JlOHHuYAuZtehnQQl0tzjyvpxZpmISkPzEAb0zx3Hk88fgSpE70Op9gIhQ0PGC3bmQdKijTjcupjwP8dP_RkR-pCIgZjDiGt1kNtIlvXiHWZpve6xlsHuMpsz0rFXV4kRaimYLKecS5ZKGOF8y1DcYE09lPLvJdx1glPNPByibfxvtY5misIm2hVTyEDHIwtC57SX7A8hcSs5S9toZ8DH7BhZb5yhfVzbf8nOevloOZCJfYCqmt53jTxX6TDEw3u2D7vCODLFCfcFw0W8Y4nn25lPfN1Af4Y1zKg16AjTdk6L-zPHLMQPzY528QhDcOfoJgLEkLAgNT-d84ssJzUh986OASdQbCfzP1RbU3jPBTnEd4FlMbCCNw-YqX4CGwYFokEa11IKBgBs7uOOzNQEFw1H4QLssiVNPbcgAA'
    # authz_code = code
    authz_code = 'AQABAAIAAACQN9QBRU3jT6bcBQLZNUj7qteCJQCSYqS77-J2XTP5KRxa4AxuzoOJy6Z7cRqyvYjeuUTMigvyLym4E0ht8m1LLLY1EpeDVTEHWaYjLgwRhYxeFPConKTd7wRh4DKqdGEP5FOQd4X7lQNCJWRMUt3CRYTlpIdILSNCSF4beB-yyPvRSFFkrSw4S8Z1lM0DS1CzrF9hLIGfwZK8Wys8G0c3vzh-gZmHG79T5yfMG25LWNdZjfDmLZZZJHuQPPWHVQuZkb-qYFlFn5QAIW5ye6LM8vmt_Uf25d-EVxfPZeo5dn66SmZIDSYw6q6dwe6n2udXEJ2z8O9F3tzqoPZGtk9-PJFmBPBierOyupX07SiOFXklAKmeo3iUG_41HmVsuPFj1NWnNSv41W9c-SXzZP_iiP_lTQgwodwYyuGreE8UN4ATVfD0Clx0YJocv1TOsfR7WfDc03d6ILmmVsYSgupAl9jgAheZek_ahYXOwEFF7y5vUtgIGhC5r7dpltN1Yvxozhq_U9a6EZqSsbKvtI_jXKItSsSHmV3y0g9_WgR-5sqNUORhIkDHRNu4XA1C7-ggAA'
    # API call to get the token ( function link ), the response is a
    # key-value dict
    user_parameters['clientId'] = 'a1cdaed8-b083-4a90-b355-0f6ebc0cd530'
    token_response = context.acquire_token_with_authorization_code(authz_code, user_parameters['redirect_uri'],
                                                                   databricks_resource_id, user_parameters['clientId'], client_secret='9=TCItQ8:UCjY33.vpcy-G8aD/3-vKJ1')#,
                                                                   #client_secret='.t1@imD9[ExzaYeRIsa?7CIB9B4=SwVF')

    # you can print all the fields in the token_response
    for key in token_response.keys():
        print(str(key) + ': ' + str(token_response[key]))
    # the tokens can be returned as a pair (or you can return the full
    # token_response)
    return token_response['refreshToken'], token_response['accessToken']


def list_cluster_with_aad_token():
    #refresh_token, access_token = get_refresh_and_access_token()
    # e.g., westus.azuredatabricks.net
    DOMAIN = 'eastus.azuredatabricks.net'
    #TOKEN = access_token # obtained above
    TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImFQY3R3X29kdlJPb0VOZzNWb09sSWgydGlFcyIsImtpZCI6ImFQY3R3X29kdlJPb0VOZzNWb09sSWgydGlFcyJ9.eyJhdWQiOiIyZmY4MTRhNi0zMzA0LTRhYjgtODVjYi1jZDBlNmY4NzljMWQiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9hMzZkZTQ0Yi01MjgyLTQ3MWUtYTE4My0wNTI1OTg3OTk1ZTkvIiwiaWF0IjoxNTcyNTM1NDM5LCJuYmYiOjE1NzI1MzU0MzksImV4cCI6MTU3MjUzOTMzOSwiYWlvIjoiNDJWZ1lCRHZqWGJlSkh0SXVKN0pSRnlCWVY4V0FBPT0iLCJhcHBpZCI6ImExY2RhZWQ4LWIwODMtNGE5MC1iMzU1LTBmNmViYzBjZDUzMCIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2EzNmRlNDRiLTUyODItNDcxZS1hMTgzLTA1MjU5ODc5OTVlOS8iLCJvaWQiOiI0YmFmYjM4Yi0yNDg2LTQ5ODAtOTk3Zi04NzNkM2ZmZTQwZjMiLCJzdWIiOiI0YmFmYjM4Yi0yNDg2LTQ5ODAtOTk3Zi04NzNkM2ZmZTQwZjMiLCJ0aWQiOiJhMzZkZTQ0Yi01MjgyLTQ3MWUtYTE4My0wNTI1OTg3OTk1ZTkiLCJ1dGkiOiIyRmRUQ2lhY0IwaVhMR3drVFB1NUFBIiwidmVyIjoiMS4wIn0.O-76C_P5MshRVMqEbdOhnJBCKYE2p38gExBO3o1Bdp9UpTVE2ipG6yIHspOA_IPKYUDFg9C-1k0cTWU6jJM_mrjiAWDxo9tjFlrGnjiGTktfTJ3ogvgPrpsMAH6Bssr0uvBLdTBZZew0T0-lS1WMmMbktcW4XWwsEcADomY0BuVlBauTzeHao2EcbPjIApdXKNpx3aeQ4QLRSZ2RzF08URMU7DYKwwy7FZJzPnVKGg6w3Xz7025kJUZcuCEqUuDjQsJ27IR4M74D7eNWAZU7wG9g5g_Ry-fe1jD4O3rdi-d70wy134kajvdm7yWMZcSeOLcbf8__EA31OGo4ryqafQ"
    BASE_URL = 'https://%s/api/2.0/token/create' % (DOMAIN)
    # set the ORG_ID if it is available.
    # otherwise, you must include DB_RESOURCE_ID in the header
    # ORG_ID = '2551639565277758'
    # information required to build the DB_RESOURCE_ID
    SUBSCRIPTION = 'e10a4dce-de40-49f1-89e8-bc0766eafc10'
    RESOURCE_GROUP = 'platone'
    WORKSPACE = 'fcadmdatabrickswsprod'
    DB_RESOURCE_ID ='/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Databricks/workspaces/%s' %(SUBSCRIPTION, RESOURCE_GROUP, WORKSPACE)

    # request header with org_id if org_id is known
    # headers_with_org_id = {
    #     'Authorization': 'Bearer ' + TOKEN,
    #     'X-Databricks-Org-Id': ORG_ID,
    # }
    # request header with resource ID if org_id is not available
    # (e.g., the workspace has not been created yet when you call the REST API)
    headers_with_resource_id = {
        'Authorization': 'Bearer ' + TOKEN,
        'X-Databricks-Azure-Workspace-Resource-Id': DB_RESOURCE_ID
    }
    body = {
        "lifetime_seconds": 900,
        "comment": "provatokenauto"
    }
    # call the API with org_id if it is known
    response = requests.post(
        BASE_URL,
        headers=headers_with_resource_id,
        json=body
    )
    print(response.status_code)
    return response.json()['token_value']

def get_authorization_code_2():
    authorization_url= 'https://login.microsoftonline.com/a36de44b-5282-471e-a183-0525987995e9/oauth2/authorize?client_id=a1cdaed8-b083-4a90-b355-0f6ebc0cd530&response_type=code&redirect_uri=http%3A%2F%2Flocalhost&response_mode=query&resource=2ff814a6-3304-4ab8-85cb-cd0e6f879c1d&state=15'
    print(authorization_url)                               
    # open a browser, here assume we use Firefox
    dr = webdriver.Chrome(executable_path=r'C:\\Users\ABS_PC\Desktop\\chromedriver\\chromedriver.exe')
    # load the user login page
    dr.get(authorization_url)
    # wait until the user login or kill the process
    code_received = False
    code = ''
    while(not code_received):
        cur_url = dr.current_url
        if cur_url.startswith(user_parameters['redirect_uri']):
            parsed = urlparse(cur_url)
            query = parse_qs(parsed.query)
            code = query['code'][0]
            state = query['state'][0]
            # throw exception if the state does not match
            if state != str(auth_state):
                raise ValueError('state does not match')
            code_received = True
            dr.close()
    if not code_received:
        print ('Error in requesting authorization code')
        dr.close()
    # authorization code is returned. If not successful,
    # then an empty code is returned
    return code