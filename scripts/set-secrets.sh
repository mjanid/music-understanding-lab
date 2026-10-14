#!/bin/zsh
# Run this yourself on your Mac after downloading the App Store Connect API key.
# It reads ~/Downloads/AuthKey_<KEYID>.p8 and stores the four repository secrets
# via the GitHub CLI. The key content is never printed.
set -euo pipefail

REPO="mjanid/music-understanding-lab"

key_files=(~/Downloads/AuthKey_*.p8(N.om))
if (( ${#key_files} == 0 )); then
  echo "No AuthKey_*.p8 found in ~/Downloads. Download the API key from App Store Connect first."
  exit 1
fi
KEY_FILE=${key_files[1]}
KEY_ID=${${KEY_FILE:t:r}#AuthKey_}
echo "Using key file ${KEY_FILE:t} (Key ID: $KEY_ID)"

read "ISSUER_ID?Issuer ID (App Store Connect > Users and Access > Integrations, above the key list): "
read "TEAM_ID?Team ID (developer.apple.com/account > Membership details, 10 characters): "

gh secret set ASC_KEY_ID    -R "$REPO" -b "$KEY_ID"
gh secret set ASC_ISSUER_ID -R "$REPO" -b "$ISSUER_ID"
gh secret set APPLE_TEAM_ID -R "$REPO" -b "$TEAM_ID"
gh secret set ASC_KEY_P8    -R "$REPO" < "$KEY_FILE"

echo
echo "Done. Secrets on $REPO:"
gh secret list -R "$REPO"
echo
echo "Keep the .p8 somewhere safe - Apple lets you download it only once."
