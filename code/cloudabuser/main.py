import argparse
from check_user_permissions import check_user_permissions
from deploy_function import deploy_function
from set_iam_binding import set_iam_binding
from update_function import update_function
from createserviceaccountkey import createserviceaccountkey

parser = argparse.ArgumentParser()
parser.add_argument("--checkperm", action="store_true", help="Skip Checking user Permissions")
parser.add_argument("--deploy", action="store_true", help="Deploy the Function")
parser.add_argument("--setiambinding", action="store_true", help="Bind IAM Policy to the Function")
parser.add_argument("--update", action="store_true", help="Updates the Existing Function")
parser.add_argument("--createsakey", action="store_true", help="Creates and Downloads a Service Account Key")
parser.add_argument("--project-id", required=True, help="Project ID")
parser.add_argument("--location", required=False, help="Function Location")
parser.add_argument("--function-name", required=False, help="Function Name")
parser.add_argument("--gsutil-uri", required=False, help="gsutil URI")
parser.add_argument("--function-entry-point", required=False, help="Function Entry Point")
parser.add_argument("--service-account", required=False, help="Service Account")
args = parser.parse_args()

access_token = input("\nEnter Access Token: ")

if args.checkperm:  
    check_user_permissions(access_token, args.project_id)

if args.deploy:    
    deploy_function(access_token, args.project_id, args.location, args.function_name, args.gsutil_uri, args.function_entry_point, args.service_account)

if args.setiambinding:
    set_iam_binding(access_token, args.location, args.function_name, args.project_id)

if args.update:
    update_function(access_token, args.project_id, args.location, args.function_name, args.gsutil_uri, args.function_entry_point, args.service_account)

if args.createsakey:
    createserviceaccountkey()