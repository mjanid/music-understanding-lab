# Music Understanding Lab → TestFlight

Builds Apple's [Music Understanding Lab](https://developer.apple.com/documentation/musicunderstanding/create-visuals-using-musicunderstanding-analysis-results)
sample (WWDC26 session 253) on a GitHub-hosted `xcode-27` runner and uploads it to
TestFlight for internal testing. No Apple silicon Mac needed.

The sample is downloaded at build time (pinned by SHA-256) and not stored in this repo.

## One-time setup

1. App Store Connect → Users and Access → Integrations → Team Keys: create a key with **Admin** role, download the `.p8` to `~/Downloads`.
2. On the Mac: `zsh scripts/set-secrets.sh` (asks for Issuer ID and Team ID, sets 4 repo secrets).
3. Run the workflow once (Actions → TestFlight → Run workflow). It registers the bundle ID `com.mjanid.musicunderstandinglab`.
4. App Store Connect → Apps → New App (iOS, that bundle ID, any unique name, any SKU).
5. TestFlight → Internal Testing → create a group, add yourself.
6. Re-run the workflow → build appears in the TestFlight app on the iPhone.

## Secrets

| Name | Content |
|---|---|
| `ASC_KEY_ID` | Key ID of the App Store Connect API key |
| `ASC_ISSUER_ID` | Issuer ID |
| `ASC_KEY_P8` | Full content of `AuthKey_<KEYID>.p8` |
| `APPLE_TEAM_ID` | 10-character Apple Developer team ID |

## Signing

Default `unsigned-archive`: archive without signing, sign at export with the cloud-managed
distribution certificate (no certificates pile up across runs). If export fails, run the
workflow manually with `signed-archive`.
