"""App Store Connect preflight for the TestFlight workflow.

1. Registers the iOS bundle ID if it does not exist yet.
2. Checks whether an App Store Connect app record exists for it.

Writes `app_exists=true|false` to $GITHUB_OUTPUT. Needs ASC_KEY_ID, ASC_ISSUER_ID,
ASC_KEY_PATH and BUNDLE_ID in the environment. Never prints key material.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt

BASE = "https://api.appstoreconnect.apple.com/v1"
KEY_ID = os.environ["ASC_KEY_ID"]
ISSUER_ID = os.environ["ASC_ISSUER_ID"]
KEY_PATH = os.environ["ASC_KEY_PATH"]
BUNDLE_ID = os.environ["BUNDLE_ID"]


def token() -> str:
    with open(KEY_PATH, encoding="utf-8") as f:
        key = f.read()
    now = int(time.time())
    return jwt.encode(
        {"iss": ISSUER_ID, "iat": now, "exp": now + 600, "aud": "appstoreconnect-v1"},
        key,
        algorithm="ES256",
        headers={"kid": KEY_ID, "typ": "JWT"},
    )


def call(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:800]
        hint = ""
        if e.code == 401:
            hint = " (check ASC_KEY_ID / ASC_ISSUER_ID / ASC_KEY_P8)"
        elif e.code == 403:
            hint = " (the API key needs the Admin role)"
        print(f"::error::App Store Connect API {method} {path} -> HTTP {e.code}{hint}: {detail}")
        sys.exit(1)


def set_output(name: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
    print(f"{name}={value}")


def main() -> None:
    found = call("GET", "/bundleIds", {"filter[identifier]": BUNDLE_ID, "limit": 200})
    exact = [b for b in found.get("data", []) if b["attributes"]["identifier"] == BUNDLE_ID]
    if exact:
        print(f"Bundle ID {BUNDLE_ID} already registered ({exact[0]['attributes'].get('platform')}).")
    else:
        call(
            "POST",
            "/bundleIds",
            body={
                "data": {
                    "type": "bundleIds",
                    "attributes": {
                        "identifier": BUNDLE_ID,
                        "name": "Music Understanding Lab",
                        "platform": "IOS",
                    },
                }
            },
        )
        print(f"Registered bundle ID {BUNDLE_ID}.")

    apps = call("GET", "/apps", {"filter[bundleId]": BUNDLE_ID})
    match = [a for a in apps.get("data", []) if a["attributes"].get("bundleId") == BUNDLE_ID]
    if match:
        print(f"App record found: {match[0]['attributes'].get('name')} (id {match[0]['id']}).")
        set_output("app_exists", "true")
    else:
        print(f"::warning::No App Store Connect app for {BUNDLE_ID} yet - will build and sign, but not upload.")
        set_output("app_exists", "false")


if __name__ == "__main__":
    main()
