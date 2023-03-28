import argparse
from google.cloud.functions_v1 import CloudFunctionsServiceClient, CloudFunction, UpdateFunctionRequest
import google.oauth2.credentials

def update_function(access_token, project_id, location, function_name, gsutil_uri, function_entry_point, service_account):
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

    request = UpdateFunctionRequest(function=function, update_mask="sourceArchiveUrl,entryPoint,runtime,serviceAccountEmail,httpsTrigger")
    print("\n[+] Cloud Function Update (--update)")
    try:
        response = client.update_function(request=request)
        print("    - Updating Cloud Function")
        print("    - Takes 1-2 minutes to update")
        result = response.result()
        print(f"    - Function Invocation URL: {url}")

    except Exception as e:
        error_message = str(e)
        if "'cloudfunctions.functions.update' denied" in error_message:
            print(f"    - You can't Update the Cloud Function {function_name} since you don't have the 'cloudfunctions.functions.update' permission")
        elif "'cloudfunctions.operations.get' denied" in error_message:
            print("    - Permission cloudfunctions.operations.get denied (Not an Issue)")
            print(f"    - Function Invocation URL: {url}")
        else:
            print(f"    - Error: {error_message}")