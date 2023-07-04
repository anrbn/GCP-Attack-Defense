<div style="display: inline-flex; align-items: center;">
    <img src="https://logos-world.net/wp-content/uploads/2021/02/Google-Cloud-Emblem.png" alt="Google Cloud Platform" width="200" height="auto">
    <h1 style="margin-left: 10px;">Google Cloud & Workspace - Attack & Defense Research</h1>
</div>


This project is committed to documenting various attack and detection vectors that may be encountered within the Google Cloud Platform (GCP) and Google Workspace. By cataloging these potential security threats, the project aims to provide well documented research for users to better understand the attack and defense mechanism in Google Cloud and Workspace. 

This project also hopes to aid professionals in further research on both Google Cloud and Workspace.

## Tools
- [gLess](https://github.com/anrbn/gLess)

## Google Cloud (GCP)
- [Cloud Function](https://github.com/anrbn/GCP-Attack-Defense/tree/main/research/Google%20Cloud/Cloud%20Function)
    - [Privilege Escalation via Cloud Functions (ID: TA0004)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/PrivEsc-via-CloudFunction.md)
    - [Defense Evasion via Source Code Concealment in Cloud Functions (ID: T1564)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Cloud/Cloud%20Function/DefEvn-via-Source-Code-Concealment.md)

## Google Workspace
- [Apps Script](https://github.com/anrbn/GCP-Attack-Defense/tree/main/research/Google%20Workspace/Apps%20Script)
    - [Persistence via Apps Script (ID: TA0004)](https://github.com/anrbn/GCP-Attack-Defense/blob/main/research/Google%20Workspace/Apps%20Script/Persistence-via-AppsScript.md)

## Questions and Issues
If you have any questions regarding any materials in this project, please don't hesitate to reach out to me via [Twitter](https://twitter.com/corvuscr0w) or [LinkedIn](https://www.linkedin.com/in/anrbnds/). I'm always happy to help and provide support. Additionally, if you come across any issues or mistakes while reading the materials/using the tools, please feel free to submit an issue on the GitHub repository, and I'll work on addressing it as soon as possible. Thank you for your support! :)

## Todo 
- [x] Tool/gLess - Code to check if user has permission to create and download "Service Account Key"
- [x] Research/CloudFunction - Cloud Function - Source Code Concealment
- [x] Tool/gLess - Code that removes reliance on any API/Service to check if certain services are enabled.
- [x] Research/CloudFunction/Source-Code-Concealment - Hiding in Plain Sight: Source Code Concealment in Cloud Functions
- [ ] Tool/gLess - Code to enable certain API/Services
- [ ] Research/CloudFunction/PrivEsc-via-CloudFunction - How is gCloud with broad roles able to enable services without even enabling Service usage API?
- [ ] Tool/gLess - Include Support for REST API 
