# Vercel deployment – fix “link not working”

Follow these steps so the **frontend** can talk to the **backend** on Vercel.

## 1. Deploy the backend (repo root)

```bash
cd /path/to/ppt_agent
vercel --prod
```

Note the URL (e.g. `https://ppt-agent-xxx.vercel.app`). This is your **backend URL**.

- Set all required env vars in **Vercel → Backend project → Settings → Environment Variables** (see `.env.example` and `VERCEL_ENV_SETUP.md`).
- Optional: set `FRONTEND_URL` to your frontend URL (e.g. `https://ppt-agent-frontend-xxx.vercel.app`). CORS also allows any `*.vercel.app` origin.

## 2. Deploy the frontend (frontend folder)

```bash
cd ppt-agent-frontend
vercel --prod
```

Note the frontend URL (e.g. `https://ppt-agent-frontend-xxx.vercel.app`).

## 3. Point frontend to backend (required)

In **Vercel → Frontend project → Settings → Environment Variables** add:

| Name           | Value                          | Environment |
|----------------|--------------------------------|------------|
| `VITE_API_URL` | `https://your-backend.vercel.app` | Production (and Preview if you use previews) |

Use your **actual backend URL** from step 1 (no trailing slash).

Then **redeploy** the frontend (Deployments → ⋮ → Redeploy), or push a new commit. Without this, the app keeps calling `http://localhost:8001` and the link will not work.

## 4. Test

- Open the **frontend** URL.
- Enter a prompt and click “Generate Presentation”.
- You should get a shareable Google Slides link.

If it still fails, check:

- Backend: `https://your-backend.vercel.app/health` returns `{"status":"healthy"}`.
- Browser dev tools (Network tab): request to `your-backend.vercel.app` is not blocked by CORS and returns 200 or a clear error.
