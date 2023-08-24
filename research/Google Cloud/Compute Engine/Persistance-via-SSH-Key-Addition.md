SSH (Secure Shell) has long been the de facto standard for secure remote access to UNIX-based systems. Traditionally, SSH relies on key-based authentication, where a user's public key is stored on the server, and the corresponding private key is held by the user. When the user attempts to connect, the server challenges the user to prove they have the corresponding private key, ensuring a secure handshake.

However, as cloud computing evolved and infrastructure scaled to unprecedented levels, managing individual SSH keys for each user and each server became a daunting task. The traditional method of manually placing public keys in the `~/.ssh/authorized_keys` file of each server was no longer feasible for large-scale deployments. There was a need for a more scalable, centralized, and automated solution.

Google Cloud Platform (GCP) came up with its innovative approach to SSH key management. Traditional SSH methods relied on individual VM configurations, which could become cumbersome and challenging to manage at scale. Recognizing these challenges, GCP introduced a centralized system, allowing for more streamlined, efficient, and secure management of SSH keys, irrespective of the number of VMs in operation. This centralized system is built upon the concept of metadata, which serves as a repository for configuration data, including SSH keys.

# Metadata: The Centralized Configuration Store

In GCP, metadata provides a unified way to store and retrieve configuration information without having to access the VM directly. This not only simplifies the management process but also enhances security by reducing direct interactions with the VMs.

Within this metadata framework, GCP offers two distinct levels:

- **Project Metadata**: This is a shared configuration space, where data can be stored and made accessible to every VM within that specific project. Among other things, both Project and Instance metadata can include Public SSH keys. When these keys are added to Project Metadata, GCP automatically populates them into the `~/.ssh/authorized_keys` file of every VM instance within that project. This ensures consistent access controls across all instances in a project. It's a powerful tool for administrators who want to maintain consistent configurations across multiple VMs.

- **Instance Metadata**: For more granular control, GCP provides instance-specific metadata. This allows for VM-specific configurations, ensuring that particular settings or data are confined to a single VM, without affecting others in the project. If an SSH key is added to an instance's metadata, it will be populated into that specific VM's `~/.ssh/authorized_keys` file. This is particularly useful for instances that require different access controls than the broader project.

By leveraging these metadata levels, GCP offers a flexible and robust system that caters to both broad and specific configuration needs, ensuring that VMs are both accessible and secure.

One of the features GCP offers is the "**Block project-wide SSH keys**" option, which can be enabled at Instance Level not Project Level. When enabled for a specific VM instance, this feature ensures that only keys specified in the Instance Metadata can be used to access that VM, overriding any keys specified at the Project level. This provides an additional layer of granularity and control, allowing administrators to set specific access controls for individual VMs.

However, GCP's innovations in the realm of SSH access don't end with metadata. As the cloud ecosystem evolved and security demands intensified, there was need for even more sophisticated access controls, this is where Google introduced OS Login.

# OS Login - A Modern Approach

**OS Login** is a feature that seamlessly integrates SSH key management with Google Cloud Identity. This integration offers a dynamic and fortified method for managing SSH access. OS Login can be enabled at both Project and Instance Level. When OS Login is activated (by setting *enable-oslogin* to *TRUE*) the conventional practice of utilizing the `~/.ssh/authorized_keys` file for SSH key storage is sidestepped. If OS Login is activated at the Project Level (by setting *enable-oslogin* to *TRUE*), it becomes the default for all VMs in that project. However, this can be overridden by setting the environment variable "*enable-oslogin*" to "*FALSE*" at the Instance level to disable OS Login.

The beauty of OS Login lies in its ability to directly link SSH keys with user or service accounts in GCP, thereby introducing an added layer of identity verification to the SSH authentication process.

Below is a attached Image which expalain the overall process discussed above.

<p><img src="https://drive.google.com/uc?id=17zLXP9Y91QunzEBuU6LdNC4o7pMB4Z8k"></p> 






CHECKTHIS
https://cloud.google.com/compute/docs/instances/ssh?_ga=2.263044300.-1952421504.1688797993

In UNIX-based VMs, one way of maintaining persistent access typically involves logging into the system and manually adding an SSH public key to the "**authorized_keys**" file. This method, while direct, can be somewhat tedious. However, in Google Cloud Platform (GCP) one can add the SSH public key directly to the **Instance Metadata** or in the **Project Metadata**. Compute Engine then automatically updates the authorized_keys file with Public key and username from metadata thus simplifying the overall process.

In GCP, Public SSH Keys can be stored at two levels: **Project Metadata** and **Instance Metadata.**

- **Project Metadata:** When keys are added to the Project Metadata, they are made available to every VM within that project. This is especially useful for administrators or teams who need consistent access across multiple VMs. However, if the option "Block project-wide SSH keys" is enabled or checked for a specific Instance. The SSH Keys in Project Metadata can't be used to login to that Instance. In such cases Keys in **Instance Metadata** or the keys in **authorized_keys** file in the VM can be used to login.

- **Instance Metadata:** Keys stored here are specific to an Individual VM. This allows for more granular control, ensuring that only designated individuals or services can access a particular instance.

> Usecase to clear any confusion
>
> Consider a scenario where a project contains multiple VMs - some for development and testing, while others for production. The development team needs access to all VMs for updates and debugging, so their keys are added to the project metadata. However, a third-party auditor requires access only to a specific production VM to review system logs. In this case, the auditor's key would be added to the instance-specific metadata of that particular VM, ensuring restricted access.

# Handling SSH Logins in Compute Engine

**SSH from Google Console:**

- **Key Generation**:
  1. The Google Cloud Console dynamically generates a temporary Private and Public Key
  2. The Public Key is added to the Instance Metadata if OS Login is enabled at Project Level. Else if OS Login is disabled or Project Metadata (depending on OS Login being Enabled or ) as well as adds the Public Key in ~/.ssh/authorized_keys inside the VM.

- **Key Validity**: The Public and Private Key are temporary. Once the SSH session ends, browser or the SSH window is closed, the Public Key is removed from the ~/.ssh/authorized_keys file from the VM. The Private Key in the browser session is also discarded.

- **Metadata**: If OS Login is disabled, Compute Engine adds the Public Key in the Project Metadata. If OS Login is enabled the Public Key is added in Instance Metadata.

- **Key Location**:

  - Public Key: ~/.ssh/authorized_keys inside the VM. 

  - Private Key: Private Key is not exposed to the user and is kept in the browser's memory for the duration of the SSH session. This is not easily retrievable, as it's stored in the browser session and is discarded after the session ends.

**SSH from gCloud:**

- **Key Generation**: gCloud takes care of Key Generation by creating Private Key (google_compute_engine) and Public Key (google_compute_engine.pub).

  If both Private Key (google_compute_engine) and Public Key (google_compute_engine.pub) already exists gCloud will use them without creating a new one.

  If either one of Private Key (google_compute_engine) or Public Key (google_compute_engine.pub) don't exist gCloud will create new Private and Public Key.

- **Key Validity**: The Public and Private Key don't have a expiration time. They remain valid until they are explicitly revoked or removed from the authorized_keys file inside the VM.

- **Metadata**: If OS Login is disabled, Compute Engine adds the Public Key in the Project Metadata. If OS Login is enabled the Public Key is added in Instance Metadata.

- **Key Location**:

  - Public Key: Local machine where gCloud was used, at ~/.ssh/google_compute_engine.pub.

    Once a new Public Key is created, the google_compute_engine.pub is not appended but overwritten.

  - Private Key: Local machine where gCloud was used, at ~/.ssh/google_compute_engine.

  ```powershell
  # Creating a Compute Instance.
  gcloud compute instances create instance-1 --zone=us-central1-a --image-family=debian-10 --image-project=debian-cloud --machine-type=e2-micro
  
  # Creating a Compute Instance with Block project-wide SSH keys enabled.
  gcloud compute instances create instance-1 --zone=us-central1-a --image-family=debian-10 --image-project=debian-cloud --machine-type=e2-micro --metadata block-project-ssh-keys=TRUE
  
  # Using gCloud to SSH into the Instance.
  gcloud compute ssh instance-1 --zone=us-central1-a
  ```

**SSH from Third Party Tools: OpenSSH client**

- **Key Generation**: In case of third party tools, the user needs to create and maintain the Keys.
  ```powershell
  
  ```
  
- **Key Validity**: The Public and Private Key don't have a expiration time. They remain valid until they are explicitly revoked or removed from the authorized_keys file.

- **Metadata**: If OS Login is disabled, the Public Key is kept in the Project Metadata. If OS Login is enabled the Public Key is kept in Instance Metadata.

- **Key Location**:
  - Public Key: Find it on your local machine at ~/.ssh/google_compute_engine.pub.
    
    Once a new Public Key is created, it's not appended but overwritten.

  - Private Key: Find it on your local machine at ~/.ssh/google_compute_engine.

  ```powershell
  # Creating a Compute Instance.
  gcloud compute instances create instance-1 --zone=us-central1-a --image-family=debian-10 --image-project=debian-cloud --machine-type=e2-micro
  
  # Creating a Compute Instance with Block project-wide SSH keys enabled.
  gcloud compute instances create instance-1 --zone=us-central1-a --image-family=debian-10 --image-project=debian-cloud --machine-type=e2-micro --metadata block-project-ssh-keys=TRUE
  
  # Using gCloud to SSH into the Instance.
  gcloud compute ssh instance-1 --zone=us-central1-a
  ```

### 1. Key Generation:

If an SSH key pair is not present, generate one using the ssh-keygen command:
```powershell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
This will generate a private key `(~/.ssh/id_rsa)` and a public key `(~/.ssh/id_rsa.pub)`.
   
### 2. Add the Public Key to GCP:
   
Option A: Using the GCP Console
- Navigate to the VM instances page in the Compute Engine.
- Click on the instance to SSH into.
- Under SSH Keys, click on Edit.
- Add the content of Public Key (~/.ssh/id_rsa.pub) to the SSH keys box.

Option B: Using gcloud

```powershell
gcloud compute instances add-metadata [INSTANCE_NAME] --zone=[ZONE] --metadata-from-file ssh-keys=~/.ssh/id_rsa.pub
```

Replace [INSTANCE_NAME] with the name of the instance and [ZONE] with the appropriate zone.

### 3. SSH into the VM:
Use the ssh command to connect to the VM.

```powershell
ssh -i ~/.ssh/id_rsa [USERNAME]@[EXTERNAL_IP]
```

Replace [USERNAME] with the username associated with the key (the email used or the default username for the OS) and [EXTERNAL_IP] with the external IP address of the VM.

# Methods to add SSH Keys for Persisting in VM (OS Login Disabled)

- **Method 1. Authorized Key File**

  Adding the Public Keys directly in the ~/.ssh/authorized_key file by logging in to the specific Instance.

- **Method 2. Project Metadata**

  Adding the Public Keys in Project Metadata which will be added to every Instance by Compute Engine.

- **Method 3. Instance Metadata**

  Adding the Public Keys in Instance Metadata which will be added to the specific Instance by Compute Engine.

<IMAGE>

It's worth noting that Compute Engine provides a security feature named "**Block project-wide SSH keys**". When activated for a VM, this feature prevents the automatic import of SSH keys from the Project Metadata, thereby rendering "Method 2" useless. However, if "Block project-wide SSH keys" is enabled/checked, Compute Engine can still import SSH keys from the Instance Metadata and add it in ~/.ssh/authorized_key file.

<IMAGE>

# How OS Login comes into the picture? how does it change the SSH key management?

# Methods to add SSH Keys for Persisting in VM (OS Login Enabled)
