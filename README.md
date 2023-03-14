**Mapping the Attack Path**

**Ways one can create a Cloud Function in GCP**

There are three ways to create a Cloud Function in GCP: 

1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

![](https://github.com/anrbn/blog/blob/main/images/6.jpg)
>fig.1
>
While Cloud Console may seem user-friendly for creating resources in GCP, we won't be using it. The reason being, creating resources in GCP often involves navigating through different pages, each with its own set of permissions. Depending on the user's level of access, they may not be able to view or access certain pages necessary to create a particular resource. It's important to have a number of permissions in place to ensure that a user can perform the actions they need to within the GCP environment. 

Our focus in this blog is on creating a Cloud Function using the least privileges possible. That's also why attackers tend to use the gCloud command and Cloud Function API (via gRPC or REST) to create resources. Furthermore, attackers mainly gain access to a GCP environment using stolen or compromised authentication tokens (auth_tokens). Cloud Console doesn't support authentication via auth_tokens. As a result, attackers may prefer to use the gCloud command or directly call the Cloud Function API via gRPC or REST API to create resources because they offer more flexibility in terms of authentication and control.

Now let's dig deeper into it.

If you're creating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code that provides access to the Service Account Token. There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

![](https://github.com/anrbn/blog/blob/main/images/7.jpg)
>fig.2

**Permission Required for Deploying a Cloud Function**

Let's start with the first step of deploying/creating a Cloud Function. As always every action in GCP requires you to have a certain amount of Permissions. Thus, let's try to find the least amount of permissions required for deploying/creating a Cloud Function. 

Here's the list of least number of permissions I found that's required to "Deploy a Cloud Function via gCloud"

<table>
  <tr>
   <td colspan="3" ><strong>Cloud Function Deploy via gCloud</strong>
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

![](https://github.com/anrbn/blog/blob/main/images/8.jpg)
>fig.3


Note: 
1. Different Project means the Source Code is uploaded to a Cloud Storage / Repository of a project different than the one being exploited. It is the attacker controlled project where the attacker has full control.
2. Last two permissions in bottom right (source.repos.get & source.repos.list) are required to be granted to the "Google Cloud Functions Service Agent" in Attacker's controlled project for it to be able to read the repository from attacker's project and upload the code in the Function. 

The format of the service account email for the Google Cloud Functions Service Agent is `service-{PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com`. Figuring out the Google Cloud Functions Service Agent email requires one to know the Project Number, which might need additional permissions. 

For gCloud 
 
<image>

Every permission mentioned in the list seems to do something which is quite clear from their name. But here's something I found really strange, why is there a need for  `cloudfunctions.functions.get` permission for creating a Cloud Function? As far as the documentation goes the description for the permission `cloudfunctions.functions.get` says view functions. ([Link](https://cloud.google.com/functions/docs/reference/iam/permissions))

Which means `cloudfunctions.functions.get` permission allows a user or service account to view metadata about a Cloud Function, such as its name, runtime, entry point, trigger settings, and other configuration details. What I guess is, it may be a default behavior of gCloud to include this permission when creating a function but it is not necessary for the creation of the function.

Using tools like gCloud can be convenient, but sometimes gCloud requires additional permissions beyond what is actually needed for the task at hand. This can result in unnecessarily permission requirements for users. 

One way to narrow down the permission requirements is to not rely on tools like gCloud at all, but to use the Cloud Function API yourself. Cloud Function API can be called via gRPC and REST APIs. Using gRPC or REST APIs can be more precise and efficient in terms of permissions to create resources like Cloud Functions. gRPC and REST API allows us to specify only the necessary permissions for the specific task.

For Cloud Function API 

<image>

That being said let's look at how to "Deploy a Cloud Function via Cloud Function API (gRPC & REST)"

**Deploying a Cloud Function via Cloud Function API (gRPC)**

gRPC is an open-source Remote Procedure Call (RPC) framework developed by Google. While REST (Representational State Transfer) is an architectural style for building web-based software systems. REST APIs are commonly used to access and manage cloud resources. 

Won't go into much details and step straight into the point. Here is the list of Permission required to successfully deploy a Cloud Function via Cloud Function API (gRPC & REST). 

<table>
  <tr>
   <td colspan="3" ><strong>Cloud Function Deploy via Cloud Function API (gRPC & REST)</strong>
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
  
![](https://github.com/anrbn/blog/blob/main/images/9.jpg)
>fig.4
  
[Note: You might need additional permissions to successfully upload code from the two sources: Local Machine and Cloud Repository via Cloud Function API (gRPC & REST).  However, for the Source: Cloud Storage, the permissions listed are the least that's required. Since it's easier to do it via Cloud Storage, why even bother with the other two? :)] 


If you take a look at the above figures (fig 3 & 4), it's clear that of the two methods for deploying a Cloud Function (using gCloud or the Cloud Function API), uploading the source code via Cloud Storage using the Cloud Function API requires the least amount of permissions and can easily be chosen over any other method. Here's a figure to understand it better. 
 
<Image 3>

<Image 4>

 
Let's call the Cloud Function API using both gRPC and REST to deploy a Cloud Function (Code Upload Source: Cloud Storage). 

Below is a code that's calling the Cloud Function API via gRPC to deploy a Cloud Function in GCP. It's using the method being create_function() from the google.cloud.functions_v1.CloudFunctionsServiceClient class. Note that for uploading the Source Code we will be using Cloud Storage, simply because it requires less number of permission than any other method (Check <Figure> ).

```python
from google.cloud.functions_v1 import CloudFunctionsServiceClient, CloudFunction, CreateFunctionRequest
import google.auth
import time

credentials, project_id = google.auth.default()

location = "us-east1"
function_name = "exfil11"
bucket_name = "anirb"
source_zip = "function.zip"
function_entry_point = "exfil"

client = CloudFunctionsServiceClient(credentials=credentials)

url = "https://{}-{}.cloudfunctions.net/{}".format(location, project_id, function_name)

function = CloudFunction(
    name="projects/{}/locations/{}/functions/{}".format(project_id, location, function_name),
    source_archive_url="gs://{}/{}".format(bucket_name, source_zip),
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


Even though a warning pops up that "Permission `cloudfunctions.operations.get` denied on resource" the Cloud Function will be successfully created. The warning is likely due to some internal operations being performed by the Cloud Function service during the creation process.  
 
The Cloud Function however will be created with just the following permissions:
* iam.serviceAccounts.actAs
* cloudfunctions.functions.create

Here's another way to call the Cloud Function API using REST. Below is a curl command which

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-to-zipped-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

```shell
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"projects/<project-id>/locations/<region>/functions/<function-name>","entryPoint":"<function-entrypoint>","runtime":"python38","serviceAccountEmail":"<service-account-email>","sourceArchiveUrl":"<gs-link-to-zipped-sourcecode>","httpsTrigger":{}}' \
  https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json

```


Let's breakdown each component required:



<table>
  <tr>
   <td>&lt;token> 
   </td>
   <td>&lt;token> is a placeholder for an actual authorization token that is required to authenticate and authorize the API request. Run the command 
"gcloud auth application-default print-access-token" to get the token.
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
   <td>The email address of the service account that will be used to run the Cloud Function. 
<p>
Choosing a Service Account with high privileges will help you Privilege Escalate easier.
   </td>
  </tr>
  <tr>
   <td>&lt;gs-link-to-zipped-sourcecode>
   </td>
   <td>The URL of the Cloud Storage archive file that contains the source code for the Cloud Function. The archive file must be in ZIP format. Example: gs://bucket-name/code.zip
   </td>
  </tr>
</table>


Once 

**Permission Required for Invoking a Cloud Function**

Creating/Deploying a Cloud Function is just the first step in the process. Making it available for invocation is the second.

When you create a Cloud Function in GCP, it is not immediately accessible for invocation. Before you can invoke the function, you need to set up the necessary IAM permissions to allow access to the function and control who has access to your Cloud Function and what they can do with it.

To set up IAM permissions for your Cloud Function, you can add one or more members to a Cloud Function's IAM policy. Members can be individual user accounts, groups of users, or service accounts. You can assign roles to these members, which determine the actions they can perform on the function. 

Now, there's a special member called `allUsers` that represents anyone on the internet. We will be granting the member : `allUsers` the role : `Cloud Function Invoker` to to Invoke the function.This will allow anyone on the internet to invoke the Cloud Function without requiring authentication.
[Note: Granting allUsers permissions to a Cloud Function, you are essentially making your Cloud Function publicly accessible to anyone who knows the URL].

In order to grant the `allUsers` member the `Cloud Function Invoker` role, the user or service account performing the operation must have certain permissions. Let's figure that out.


The code will query the metadata server and retrieve an access token and then print that token to the logs and response body when a request is made to that specific endpoint.
