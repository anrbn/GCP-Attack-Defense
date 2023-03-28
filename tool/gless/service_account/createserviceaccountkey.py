import grpc
from google.protobuf.json_format import MessageToJson
from google.iam.admin.v1.iam_pb2 import CreateServiceAccountKeyRequest, ServiceAccountPrivateKeyType, KEY_ALG_RSA_2048
from google.iam.admin.v1.iam_pb2_grpc import IAMStub
from service_account.access_token_auth_interceptor import AccessTokenAuthInterceptor

def createserviceaccountkey(project_id):
    print("\n[+] Service Account Key Create & Download (--createsakey)")
    service_account_email = input('    - Enter Service Account Email: ')
    access_token = input('    - Enter Access Token: ')
    output_filename = f"{service_account_email}.json"

    channel = grpc.secure_channel("iam.googleapis.com:443", grpc.ssl_channel_credentials())
    interceptor = AccessTokenAuthInterceptor(access_token)
    channel = grpc.intercept_channel(channel, interceptor)

    stub = IAMStub(channel)

    request = CreateServiceAccountKeyRequest(
        name=f"projects/{project_id}/serviceAccounts/{service_account_email}",
        private_key_type=ServiceAccountPrivateKeyType.TYPE_GOOGLE_CREDENTIALS_FILE,
        key_algorithm=KEY_ALG_RSA_2048
    )

    response = stub.CreateServiceAccountKey(request)

    try:
        key_data = response.private_key_data
        with open(output_filename, "wb") as key_file:
            key_file.write(key_data)
        print('    - Created JSON Key')
        print(f'    - Saved {service_account_email} key to {service_account_email}.json')

    except Exception as e:
        error_message = str(e)
        if "'iam.serviceAccountKeys.create' denied" in error_message:
            print("    - Permission iam.serviceAccountKeys.create denied")
            print(f"    - You can't create and download the Service Account Key since you don't have the 'iam.serviceAccountKeys.create' Permission")
        else:
            print(f"    - Error: {str(e)}")