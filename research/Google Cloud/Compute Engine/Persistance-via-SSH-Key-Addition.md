CHECKTHIS

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




**SSH from the Console:**
- Key Generation: The Google Cloud Console dynamically generates a temporary key pair for the SSH session.

- Key Validity: The Public and Private Key are temporary. Once the SSH session ends, browser or the SSH window is closed, the Public Key is removed from the ~/.ssh/authorized_keys file. The Private Key in the browser session is also discarded.
 

- Key Location:
  - Public Key: Public Key can viewed in ~/.ssh/authorized_keys or by quering the Metadata Server. 
    ```shell
    curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/ssh-keys" -H "Metadata-Flavor: Google"
    ```
  - Private Key: Private Key is not exposed to the user and is kept in the browser's memory for the duration of the SSH session. This is not easily retrievable, as it's stored in the browser session and is discarded after the session ends.

**SSH from gCloud:**
- Key Generation: The gCloud tool will create **google_compute_engine** (Private Key) and **google_compute_engine.pub** (Public Key) in your ~/.ssh/ directory.
  
  If both **google_compute_engine** (Private Key) and **google_compute_engine.pub** (Public Key) already exists gCloud will use them without creating a new one.
  
  If either one of **google_compute_engine** (Private Key) or **google_compute_engine.pub** (Public Key) don't exist gCloud will create new Private and Public Key.

- Key Validity: The Public and Private Key don't have a expiration time. They remain valid until they are explicitly revoked or removed from the authorized_keys file.

- Metadata: If OS Login is disabled, the Public Key is kept in the Project Metadata. If OS Login is enabled the Public Key is kept in Instance Metadata.

- Key Location:
  - Public Key: Find it on your local machine at ~/.ssh/google_compute_engine.pub or C:\Users\<username>\.ssh (Windows).
    
    Once a new Public Key is created, it's not appended but overwritten.
  
  - Private Key: Find it on your local machine at ~/.ssh/google_compute_engine (Unix) or C:\Users\<username>\.ssh (Windows).
