**Mapping the Attack Path**

**Ways one can create a Cloud Function in GCP**

There are three ways to create a Cloud Function in GCP: 

1. Cloud Console
2. gCloud Command
3. Cloud Function API (REST & gRPC)

&lt;image>

While Cloud Console may seem user-friendly for creating resources in GCP, we won't be using it. The reason being, creating resources in GCP often involves navigating through different pages, each with its own set of permissions. Depending on the user's level of access, they may not be able to view or access certain pages necessary to create a particular resource. It's important to have a number of permissions in place to ensure that a user can perform the actions they need to within the GCP environment. 

Our focus in this blog is on creating a Cloud Function using the least privileges possible. That's also why attackers tend to use the gCloud command and REST API to create resources. Furthermore, attackers mainly gain access to a GCP environment using stolen or compromised authentication tokens (auth_tokens). Cloud Console doesn't support authentication via auth_tokens. As a result, attackers may prefer to use the gCloud command or REST API to create resources because they offer more flexibility in terms of authentication and control.

Now let’s dig deeper into it.

If you're creating a Cloud Function in GCP, you can use **Cloud Console, gCloud Command, **or** Cloud Function API** to do so. Regardless of the method you choose, you will need to upload the code that provides access to the Service Account Token. There are three different ways to upload the code:

1. Local Machine
2. Cloud Storage
3. Cloud Repository

&lt;image>

**Permission Required for Deploying a Cloud Function**

Let’s start with the first step of deploying/creating a Cloud Function. As always every action in GCP requires you to have a certain amount of Permissions. Thus, let's try to find the least amount of permissions required for deploying/creating a Cloud Function. 

Here’s the list of Least number of Permissions I found that’s required to “Deploy a Cloud Function via gCloud”

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


Note: 
1. Different Project means the Source Code is uploaded to a Cloud Storage / Repository of a project different than the one being exploited. Project where the Attacker has full control.
2. Last two permissions in bottom right (source.repos.get & source.repos.list) are required to be granted to the “Google Cloud Functions Service Agent” in Attacker’s controlled project for it to be able to read the repository and upload the code in the Function. 

The format of the service account email for the Google Cloud Functions Service Agent is service-{PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com. Figuring out the Google Cloud Functions Service Agent email requires one to know the Project Number, which might need additional permissions. 

For gCloud 
 
&lt;image>

Every permission mentioned in the list seems to do something which is quite clear from their name. But here’s something I found really strange, why is there a need for  “cloudfunctions.functions.get” permission for creating a Cloud Function? As far as the documentation goes the description for the permission “cloudfunctions.functions.get” says view functions. ([Link](https://cloud.google.com/functions/docs/reference/iam/permissions))
