# What to change in Vercel when the serverless function crashes

## 1. Check Runtime Logs (do this first)

- In your **ppt-agent** project, open **Deployments** → click the latest deployment.
- Click **Runtime Logs** (or **Functions** → select the function → Logs).
- Look for the **exact error** (traceback or message). That tells you if it’s:
  - Missing env vars
  - Wrong Python version
  - Import/code error

## 2. Environment variables (backend project)

In **Settings → Environment Variables** for the **backend** project, ensure these are set for **Production** (and Preview if you use it):

**Required:**

- `ANTHROPIC_API_KEY`
- Google credentials (see `VERCEL_ENV_SETUP.md`):  
  `GOOGLE_PROJECT_ID`, `GOOGLE_PRIVATE_KEY`, `GOOGLE_CLIENT_EMAIL`, `GOOGLE_TOKEN_URI`, etc., **or** base64 `GOOGLE_CREDENTIALS_JSON`
- `DEFAULT_PRESENTATION_ID`
- `GOOGLE_DRIVE_FOLDER_ID` (optional but recommended)

**Optional:**

- `FRONTEND_URL` – your frontend URL (e.g. `https://ppt-agent-frontend.vercel.app`) for CORS.  
  CORS also allows any `*.vercel.app` origin.

After adding or changing variables, **redeploy** (Deployments → ⋮ → Redeploy).

## 3. Python version

- **Settings → General** (or **Functions**).
- If available, set **Python Version** to **3.12** (or 3.11) to match your local setup.
- Save and redeploy.

## 4. Function timeout and memory (if needed)

- **Settings → Functions** (or per-function config).
- Increase **Max Duration** if generation often times out (e.g. 60s).
- Increase **Memory** if you see out-of-memory errors.

## 5. Code fix already applied

The crash was likely because Vercel’s Python runtime expects an **ASGI `app`** (your FastAPI app), but the project was exporting a **Lambda-style `handler`** (Mangum). The code was updated so that **on Vercel** only the FastAPI **`app`** is exported. After pulling the latest code and redeploying, the function should start correctly.

## 6. After changing anything

1. **Redeploy**: Deployments → ⋮ → **Redeploy** (or push a new commit).
2. Test: `https://ppt-agent.vercel.app/health` should return `{"status":"healthy"}`.
3. If it still crashes, use **Runtime Logs** from step 1 to see the new error.
