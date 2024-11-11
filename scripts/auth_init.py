# Python script for creating or verifying an Azure application registration.
# If an application with the specified ID exists, it will be verified; otherwise, a new 
# application will be created. The script also adds a client secret to the application 
# and updates environment variables for Azure Developer CLI with relevant credentials.
import argparse
import subprocess

from azure.identity import AzureDeveloperCliCredential
import urllib3

# Function to get authorization headers using Azure Developer CLI credentials
def get_auth_headers(credential):
    return {
        "Authorization": "Bearer "
        + credential.get_token("https://graph.microsoft.com/.default").token
    }

# Function to check if an Azure application exists using the provided application ID
def check_for_application(credential, app_id):
    resp = urllib3.request(
        "GET",
        f"https://graph.microsoft.com/v1.0/applications/{app_id}",
        headers=get_auth_headers(credential),
    )
    if resp.status != 200:
        print("Application not found")
        return False
    return True


# Function to create a new Azure application registration
def create_application(credential):
    resp = urllib3.request(
        "POST",
        "https://graph.microsoft.com/v1.0/applications",
        headers=get_auth_headers(credential),
        json={
            "displayName": "WebApp",
            "signInAudience": "AzureADandPersonalMicrosoftAccount",
            "web": {
                "redirectUris": ["http://localhost:5000/.auth/login/aad/callback"],
                "implicitGrantSettings": {"enableIdTokenIssuance": True},
            },
        },
        timeout=urllib3.Timeout(connect=10, read=10),
    )

    app_id = resp.json()["id"]
    client_id = resp.json()["appId"]

    return app_id, client_id

# Function to add a client secret to the application and retrieve the secret value
def add_client_secret(credential, app_id):
    resp = urllib3.request(
        "POST",
        f"https://graph.microsoft.com/v1.0/applications/{app_id}/addPassword",
        headers=get_auth_headers(credential),
        json={"passwordCredential": {"displayName": "WebAppSecret"}},
        timeout=urllib3.Timeout(connect=10, read=10),
    )
    client_secret = resp.json()["secretText"]
    return client_secret

# Function to update environment variables in the Azure Developer CLI environment
def update_azd_env(name, val):
    subprocess.run(f"azd env set {name} {val}", shell=True)

# Main function to parse arguments and perform application setup or check
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create an App Registration and client secret (if not already created)",
        epilog="Example: auth_update.py",
    )
    parser.add_argument(
        "--appid",
        required=False,
        help="Optional. ID of registered application. If provided, this script just makes sure it exists.",
    )
    args = parser.parse_args()

    credential = AzureDeveloperCliCredential()

    # If app ID is provided, check if the application exists
    if args.appid and args.appid != "no-id":
        print(f"Checking if application {args.appid} exists")
        if check_for_application(credential, args.appid):
            print("Application already exists, not creating new one.")
            exit(0)

    # If app does not exist, create a new application registration
    print("Creating application registration")
    app_id, client_id = create_application(credential)

    # Add a client secret to the application
    print(f"Adding client secret to {app_id}")
    client_secret = add_client_secret(credential, app_id)

    # Update environment variables for the application ID, client ID, and client secret
    print("Updating azd env with AUTH_APP_ID, AUTH_CLIENT_ID, AUTH_CLIENT_SECRET")
    update_azd_env("AUTH_APP_ID", app_id)
    update_azd_env("AUTH_CLIENT_ID", client_id)
    update_azd_env("AUTH_CLIENT_SECRET", client_secret)
