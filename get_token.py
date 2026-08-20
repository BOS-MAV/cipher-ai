import base64
import json
import requests
import getpass

baseurl = "https://phenomics.va.ornl.gov"

username = input("CIPHER client ID: ").strip()
pw = getpass.getpass("CIPHER client secret: ").strip()

credential = base64.b64encode(
    f"{username}:{pw}".encode("utf-8")
).decode("utf-8")

headers = {
    "content-type": "application/x-www-form-urlencoded",
    "authorization": f"Basic {credential}",
    "accept": "application/json"
}

payload = {
    "grant_type": "client_credentials"
}

result = requests.post(
    f"{baseurl}/auth/oauth2/token",
    headers=headers,
    data=payload,
    timeout=30
)

print("HTTP status:", result.status_code)
print(result.text)

if result.ok:
    data = result.json()
    print("\nBearer token:")
    print("Bearer " + data["access_token"])