import os
from google.oauth2 import service_account
import googleapiclient.discovery
import google.oauth2.credentials
import base64

def createserviceaccountkey():
    print("\n[+] Service Account Key Create & Download (--createsakey)")
    service_account_email = input('    - Enter Service Account Email: ')
    access_token = input('    - Enter Access Token: ')
    output_filename = f"{service_account_email}.json"

    credentials = google.oauth2.credentials.Credentials(access_token)
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    key = service.projects().serviceAccounts().keys().create(
        name='projects/-/serviceAccounts/' + service_account_email, body={}
    ).execute()

    if not key.get('disabled', False):
        print('    - Created JSON Key')
        json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')
        with open(output_filename, 'w') as key_file:
            key_file.write(json_key_file)
        print(f'    - Saved {service_account_email} key to {service_account_email}.json')

    else:
        print('    - Failed to create key')