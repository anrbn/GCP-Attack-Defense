from google.iam.v1.policy_pb2 import Policy, Binding
from google.cloud.functions_v1 import CloudFunctionsServiceClient
import google.oauth2.credentials

#------change this--------
location = "us-east1"
function_name = "exfil11"
project_id="nnnn-374620"
#-------------------------

access_token = input('Enter Access Token: ')
credentials = google.oauth2.credentials.Credentials(access_token)
client = CloudFunctionsServiceClient(credentials=credentials)

name="projects/{}/locations/{}/functions/{}".format(project_id, location, function_name)

binding = Binding(
    role="roles/cloudfunctions.invoker",
    members=["allUsers"],
)

policy = Policy(bindings=[binding])

response = client.set_iam_policy(request={"resource": name, "policy": policy})
print("[+] Done.")
