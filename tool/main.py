import argparse
import sys
from permission.check_user_permissions import check_user_permissions
from permission.set_iam_binding import set_iam_binding
from functions.deploy_function import deploy_function
from functions.delete_function import delete_function
from functions.update_function import update_function
from service_account.createserviceaccountkey import createserviceaccountkey
from functions.list_functions import list_functions

parser = argparse.ArgumentParser()
parser.add_argument("--checkperm", action="store_true", help="Skip Checking user Permissions")
parser.add_argument("--list", action="store_true", help="List Cloud Functions")
parser.add_argument("--deploy", action="store_true", help="Deploy a Function")
parser.add_argument("--update", action="store_true", help="Updates an Existing Function")
parser.add_argument("--delete", action="store_true", help="Deletes an Existing Function")
parser.add_argument("--createsakey", action="store_true", help="Creates and Downloads a Service Account Key")
parser.add_argument("--setiambinding", type=str, help="Bind IAM Policy to a Function and specify the principal name (e.g., 'allUsers', 'allAuthenticatedUsers')")
parser.add_argument("--project-id", required=True, help="Project ID")
parser.add_argument("--location", required=False, help="Function Location")
parser.add_argument("--function-name", required=False, help="Function Name")
parser.add_argument("--gsutil-uri", required=False, help="gsutil URI")
parser.add_argument("--function-entry-point", required=False, help="Function Entry Point")
parser.add_argument("--service-account", required=False, help="Service Account")
args = parser.parse_args()

if args.createsakey:
    if args.checkperm or args.deploy or args.setiambinding or args.update or args.delete or args.list:
        print("Error: --createsakey cannot be used with any other arguments.")
        sys.exit(1)
    createserviceaccountkey(args.project_id)
else:
    access_token = input("\nEnter Access Token: ")

    if args.checkperm:  
        check_user_permissions(access_token, args.project_id)

    if args.deploy:
        if args.update or args.delete or args.createsakey:
            print("Error: --deploy cannot be used with --update --createsakey & --delete argument.")
            sys.exit(1)
        deploy_function(access_token, args.project_id, args.location, args.function_name, args.gsutil_uri, args.function_entry_point, args.service_account)

    if args.setiambinding:
        if args.delete or args.createsakey:
            print("Error: --setiambinding cannot be used with  --createsakey & --delete argument.")
            sys.exit(1)
        principalname = args.setiambinding
        set_iam_binding(access_token, args.location, args.function_name, args.project_id, principalname)

    if args.update:
        if args.deploy or args.delete or args.createsakey:
            print("Error: --update cannot be used with --deploy --createsakey & -delete argument.")
            sys.exit(1)
        update_function(access_token, args.project_id, args.location, args.function_name, args.gsutil_uri, args.function_entry_point, args.service_account)
    
    if args.delete:
        if args.deploy or args.setiambinding or args.update or args.createsakey:
            print("Error: --delete cannot be used with --deploy, --createsakey , --setiambinding & --update argument.")
            sys.exit(1)
        delete_function(access_token, args.project_id, args.location, args.function_name)

    if args.list:
        if args.deploy or args.setiambinding or args.update or args.delete or args.createsakey:
            print("Error: --list cannot be used with --deploy, --update, --delete, --setiambinding, --createsakey  & --update argument.")
            sys.exit(1)
        list_functions(access_token, args.project_id)


