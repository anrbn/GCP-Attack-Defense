Before Moving forward clear the following 
Instance Metadata:
Resource Metadata:
Project Metadata:
VM Metadata:

In UNIX-based VMs, one way of maintaining persistent access typically involves logging into the system and manually adding an SSH public key to the "**authorized_keys**" file. This method, while direct, can be somewhat tedious. However, in Google Cloud Platform (GCP) one can add the SSH public key directly to the **Instance Metadata** or in the **Project Metadata**. GCP then automatically updates the authorized_keys file thus simplifying the overall process.

In GCP, Public SSH Keys can be stored at two levels: **Project Metadata** and **Instance Metadata.**

- **Project Metadata:** When keys are added to the Project Metadata, they are made available to every VM within that project. This is especially useful for administrators or teams who need consistent access across multiple VMs. However, if the option "Block project-wide SSH keys" is enabled or checked for a specific Instance. The SSH Keys in Project Metadata can't be used to login to that Instance. In such cases Keys in **Instance Metadata** or the keys in **authorized_keys** file in the VM can be used to login.

- **Instance Metadata:** Keys stored here are specific to an Individual VM. This allows for more granular control, ensuring that only designated individuals or services can access a particular instance.

What is default GCP Behvaiour in case of 
- SSH from the Console:
- SSH from the gCloud:

Take into account Windows
https://cloud.google.com/compute/docs/instances/ssh?_ga=2.263044300.-1952421504.1688797993

Here's an Usecase to clear the confusion.

Consider a scenario where a project contains multiple VMs - some for development and testing, while others for production. The development team needs access to all VMs for updates and debugging, so their keys are added to the project metadata. However, a third-party auditor requires access only to a specific production VM to review system logs. In this case, the auditor's key would be added to the instance-specific metadata of that particular VM, ensuring restricted access.

How OS Login comes into the picture? how does it change the SSH key management?
