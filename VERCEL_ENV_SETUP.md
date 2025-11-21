# Vercel Environment Variables Setup Guide

## Step-by-Step Guide to Set Environment Variables in Vercel

### 1. Access Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and log in
2. Select your project
3. Go to **Settings** → **Environment Variables**

### 2. Required Environment Variables Checklist

#### ✅ Anthropic API Key (REQUIRED)
- **Variable Name:** `ANTHROPIC_API_KEY`
- **Value:** Your Anthropic API key (starts with `sk-ant-...`)
- **Environments:** Production, Preview, Development

#### ✅ Google Service Account Credentials (REQUIRED - Choose ONE naming convention)

**Option A: Use `GOOGLE_*` prefix (Recommended)**
- `GOOGLE_PROJECT_ID` = `pptai-478322`
- `GOOGLE_PRIVATE_KEY_ID` = `844ed9d25049bbec32be4bdd728f29a6234d462c`
- `GOOGLE_PRIVATE_KEY` = `-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n` (full key with newlines)
- `GOOGLE_CLIENT_EMAIL` = `ppt-agent-service@pptai-478322.iam.gserviceaccount.com`
- `GOOGLE_CLIENT_ID` = `114053863238338035179`
- `GOOGLE_AUTH_URI` = `https://accounts.google.com/o/oauth2/auth`
- `GOOGLE_TOKEN_URI` = `https://oauth2.googleapis.com/token` ⚠️ **IMPORTANT: This is often missing!**
- `GOOGLE_AUTH_PROVIDER_X509_CERT_URL` = `https://www.googleapis.com/oauth2/v1/certs`
- `GOOGLE_CLIENT_X509_CERT_URL` = `https://www.googleapis.com/robot/v1/metadata/x509/ppt-agent-service%40pptai-478322.iam.gserviceaccount.com`
- `GOOGLE_UNIVERSE_DOMAIN` = `googleapis.com`

**Option B: Use direct field names (Alternative)**
- `project_id` = `pptai-478322`
- `private_key_id` = `844ed9d25049bbec32be4bdd728f29a6234d462c`
- `private_key` = `-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n`
- `client_email` = `ppt-agent-service@pptai-478322.iam.gserviceaccount.com`
- `client_id` = `114053863238338035179`
- `auth_uri` = `https://accounts.google.com/o/oauth2/auth`
- `token_uri` = `https://oauth2.googleapis.com/token` ⚠️ **IMPORTANT: This is often missing!**
- `auth_provider_x509_cert_url` = `https://www.googleapis.com/oauth2/v1/certs`
- `client_x509_cert_url` = `https://www.googleapis.com/robot/v1/metadata/x509/ppt-agent-service%40pptai-478322.iam.gserviceaccount.com`
- `universe_domain` = `googleapis.com`

#### ✅ Application Configuration (REQUIRED)
- `DEFAULT_PRESENTATION_ID` = `1ssIEyRV9ARbPZcKoUcl1sneIlUsW_p-ipRl7KnRRCDk`
- `GOOGLE_DRIVE_FOLDER_ID` = `1OUSgOEPTy9Bt3nd15ZHH5DgvCho2QUwS`

#### ⚙️ Optional Configuration
- `AGENT_MODEL` = `claude-3-5-sonnet-20241022` (default if not set)
- `AGENT_MAX_ITERATIONS` = `20` (default if not set)

### 3. How to Add Environment Variables in Vercel

1. In **Environment Variables** page, click **Add New**
2. Enter the **Key** (variable name)
3. Enter the **Value** (variable value)
4. Select **Environments** (Production, Preview, Development)
5. Click **Save**
6. Repeat for each variable

### 4. Important Notes

#### ⚠️ Private Key Format
The `GOOGLE_PRIVATE_KEY` (or `private_key`) must include:
- `-----BEGIN PRIVATE KEY-----` at the start
- `-----END PRIVATE KEY-----` at the end
- All the content in between
- Newlines should be preserved (use `\n` if pasting as a single line)

**Example:**
```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDNj4SzvPQQpUHM
... (all lines)
-----END PRIVATE KEY-----
```

#### ⚠️ Most Common Missing Variable
**`GOOGLE_TOKEN_URI` or `token_uri`** is often missing!
- **Value:** `https://oauth2.googleapis.com/token`
- This is required for Google API authentication

### 5. Verify Your Environment Variables

After setting all variables:

1. **Redeploy** your application (or wait for auto-deploy)
2. Visit: `https://your-project.vercel.app/debug/env`
3. Check the response - it will show:
   - Which variables are SET
   - Which variables are MISSING
   - Validation status
   - Specific error messages

### 6. Quick Copy-Paste Checklist

Copy these values from your `service_account.json` file:

```bash
# From your service_account.json:
project_id: "pptai-478322"
private_key_id: "844ed9d25049bbec32be4bdd728f29a6234d462c"
private_key: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email: "ppt-agent-service@pptai-478322.iam.gserviceaccount.com"
client_id: "114053863238338035179"
auth_uri: "https://accounts.google.com/o/oauth2/auth"
token_uri: "https://oauth2.googleapis.com/token"  # ⚠️ Don't forget this!
auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/ppt-agent-service%40pptai-478322.iam.gserviceaccount.com"
universe_domain: "googleapis.com"
```

### 7. Troubleshooting

#### If `/debug/env` shows variables as MISSING:
1. Check variable names (case-sensitive!)
2. Make sure you selected the right environment (Production/Preview)
3. Redeploy after adding new variables

#### If validation still fails:
1. Check the `/debug/env` endpoint for specific error messages
2. Verify `token_uri` is set correctly
3. Verify `private_key` includes BEGIN/END markers
4. Check Vercel logs for detailed errors

### 8. After Setting Variables

1. **Redeploy** your application
2. Test the root endpoint: `https://your-project.vercel.app/`
3. Test the health endpoint: `https://your-project.vercel.app/health`
4. Check debug endpoint: `https://your-project.vercel.app/debug/env`

---

## Quick Reference: All Required Variables

| Variable | Required? | Example Value |
|----------|-----------|---------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | `sk-ant-...` |
| `GOOGLE_PROJECT_ID` or `project_id` | ✅ Yes | `pptai-478322` |
| `GOOGLE_PRIVATE_KEY` or `private_key` | ✅ Yes | `-----BEGIN PRIVATE KEY-----\n...` |
| `GOOGLE_CLIENT_EMAIL` or `client_email` | ✅ Yes | `ppt-agent-service@...` |
| `GOOGLE_TOKEN_URI` or `token_uri` | ✅ Yes | `https://oauth2.googleapis.com/token` |
| `GOOGLE_PRIVATE_KEY_ID` or `private_key_id` | ✅ Yes | `844ed9d...` |
| `GOOGLE_CLIENT_ID` or `client_id` | ✅ Yes | `114053863238338035179` |
| `GOOGLE_AUTH_URI` or `auth_uri` | ✅ Yes | `https://accounts.google.com/o/oauth2/auth` |
| `GOOGLE_AUTH_PROVIDER_X509_CERT_URL` or `auth_provider_x509_cert_url` | ✅ Yes | `https://www.googleapis.com/oauth2/v1/certs` |
| `GOOGLE_CLIENT_X509_CERT_URL` or `client_x509_cert_url` | ✅ Yes | `https://www.googleapis.com/robot/v1/metadata/x509/...` |
| `GOOGLE_UNIVERSE_DOMAIN` or `universe_domain` | ✅ Yes | `googleapis.com` |
| `DEFAULT_PRESENTATION_ID` | ✅ Yes | `1ssIEyRV9ARbPZcKoUcl1sneIlUsW_p-ipRl7KnRRCDk` |
| `GOOGLE_DRIVE_FOLDER_ID` | ✅ Yes | `1OUSgOEPTy9Bt3nd15ZHH5DgvCho2QUwS` |
| `AGENT_MODEL` | ⚙️ Optional | `claude-3-5-sonnet-20241022` |
| `AGENT_MAX_ITERATIONS` | ⚙️ Optional | `20` |

---

**Next Steps:** After setting all variables, commit and push the code changes, then test the `/debug/env` endpoint!

