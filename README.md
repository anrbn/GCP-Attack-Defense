# Cloud Function Abuse Detection


### Ways one can create a Cloud Function

- Google Cloud Console: You can create Cloud Functions using the **Cloud Console**, which is a web-based interface for managing your GCP resources. To create a new function, navigate to the Cloud Functions section of the console and click the "Create function" button. You can then follow the prompts to configure your function and deploy it to the cloud.
- gcloud CLI: You can use the gcloud command-line interface (CLI) to create, deploy, and manage Cloud Functions. The gcloud CLI provides a set of command-line tools that you can use to interact with GCP services, including Cloud Functions. 
- REST API: You can also use the Cloud Functions REST API to create and manage functions programmatically. The REST API provides a set of HTTP endpoints that you can use to perform various operations on your functions, such as creating, deploying, updating, and deleting functions.

Lets map these three pathways. 

![](https://github.com/anrbn/blog/blob/main/images/1.jpg)

There are three different ways one can take to create Google Cloud Functions:

- Deploy from a local machine: One can deploy Cloud Functions directly from their local development environment using the Cloud SDK command-line tool. This method requires the Cloud SDK to be installed on the user's computer.

- Deploy from Cloud Storage: One can also deploy Cloud Functions by uploading the function's code as a ZIP archive to Cloud Storage. Once the code is uploaded, a Cloud Function can be created that points to the ZIP archive location in Cloud Storage.

- Deploy from a source repository: One can set up a continuous deployment pipeline that automatically deploys their Cloud Function whenever changes are pushed to a specific branch of their code repository.

![](https://github.com/anrbn/blog/blob/main/images/1.jpg)

Overall, each deployment option has different permission requirements. Let's map that as well.

![](https://github.com/anrbn/blog/blob/main/images/2.jpg)
