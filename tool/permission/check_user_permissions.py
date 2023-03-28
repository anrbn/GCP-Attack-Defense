import google.oauth2.credentials
from googleapiclient import discovery
from googleapiclient.errors import HttpError

def check_user_permissions(access_token, project_id):
    
    credentials = google.oauth2.credentials.Credentials(access_token)
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    resource = f"{project_id}"
    permissions = [
        "iam.serviceAccounts.actAs",
        "cloudfunctions.functions.create",
        "cloudfunctions.functions.update",
        "cloudfunctions.functions.delete",
        "cloudfunctions.functions.list",
        "cloudfunctions.functions.setIamPolicy",   
    ]

    body = {
        "permissions": permissions
    }

    print(f"\n[+] Permission Check (--checkperm)")

    try:
        response = service.projects().testIamPermissions(resource=resource, body=body).execute()

        granted_permissions = response.get("permissions", [])

        granted = []
        for permission in permissions:
            if permission in granted_permissions:
                granted.append(permission)
        if granted:
            #print("[+] Granted Permissions:")
            print("    Granted Permissions:")
            for permission in granted:
                #print(f"    - {permission}")
                print(f"        + {permission}")

        not_granted = set(permissions) - set(granted_permissions)
        if not_granted:
            #print("[!] Not Granted Permissions:")
            print("    Non Granted Permissions:")
            for permission in not_granted:
                print(f"        - {permission}")

        if "iam.serviceAccounts.actAs" in granted_permissions and "cloudfunctions.functions.create" in granted_permissions:
            print("\n[+] Cloud Function can be Deployed.") 
            print("    Run the following command to deploy a Cloud Function.")
            print('    main.py --project-id abc-123456 --location us-east1 --function-name function1 --gsutil-uri gs://bucket/function.zip --function-entry-point function --service-account 1234567890-compute@developer.gserviceaccount.com --deploy')

        else:
            print("\n[!] Cloud Function can't be Deployed.")

        if "iam.serviceAccounts.actAs" in granted_permissions and "cloudfunctions.functions.update" in granted_permissions:
            print("\n[+] Cloud Function can be Updated.")
            print("    Run the following command to update a Cloud Function.")
            print('    main.py --project-id abc-123456 --location us-east1 --function-name function1 --gsutil-uri gs://bucket/function.zip --function-entry-point function --service-account 1234567890-compute@developer.gserviceaccount.com --update')
        else:
            print("\n[!] Cloud Function can't be Updated.")

        if "cloudfunctions.functions.delete" in granted_permissions:
            print("\n[+] Cloud Function can be Deleted.")
            print("    Run the following command to delete a Cloud Function.")
            print('    main.py --project-id abc-123456 --location us-east1 --function-name function1 --delete')
        else:
            print("\n[!] Cloud Function can't be Deleted.")

        if "cloudfunctions.functions.list" in granted_permissions:
            print("\n[+] Cloud Functions can be Listed.")
            print("    Run the following command to list Cloud Functions.")
            print('    main.py --project-id abc-123456 --list')
        else:
            print("\n[!] Cloud Functions can't be Listed.")

        if "cloudfunctions.functions.setIamPolicy" in granted_permissions:
            print("\n[+] IAM Policy can be Binded to the Cloud Function.")
            print("    Run the following command to Bind an IAM Policy to the Cloud Function.")
            print('    main.py --project-id abc-123456 --location us-east1 --function-name function1 --setiambinding allUsers')
        else:
            print("\n[!] IAM Policy cannot be Binded to the Cloud Function.")

    except HttpError as error:
        print(f"\n[!] Error!: {error}")
        print("[!] Please check your access token and permissions and try again.")
