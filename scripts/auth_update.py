# Python script to update the redirect URIs for an Azure application registration.
# Uses the Azure Developer CLI credentials to authenticate and make an API request
# to update the redirect URIs for the specified application ID.
import argparse

from azure.identity import AzureDeveloperCliCredential
import urllib3

# Function to update the redirect URIs for a specified application
def update_redirect_uris(credential, app_id, uri):
    urllib3.request(
        "PATCH",
        f"https://graph.microsoft.com/v1.0/applications/{app_id}",
        headers={
            "Authorization": "Bearer "
            + credential.get_token("https://graph.microsoft.com/.default").token,
        },
        json={
            "web": {
                "redirectUris": [
                    "http://localhost:5000/.auth/login/aad/callback",
                    f"{uri}/.auth/login/aad/callback",
                ]
            }
        },
    )

# Main function to parse arguments and initiate the update process
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add a redirect URI to a registered application",
        epilog="Example: auth_update.py --appid 123 --uri https://abc.azureservices.net",
    )
    parser.add_argument(
        "--appid",
        required=False,
        help="Required. ID of the application to update.",
    )
    parser.add_argument(
        "--uri",
        required=False,
        help="Required. URI of the deployed application.",
    )
    args = parser.parse_args()

    credential = AzureDeveloperCliCredential()

    print(
        f"Updating application registration {args.appid} with redirect URI for {args.uri}"
    )
    update_redirect_uris(credential, args.appid, args.uri)
