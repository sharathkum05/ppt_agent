# Deploy the frontend so you see the landing page (not just the API JSON)

Right now only the **backend** is deployed. Visiting your Vercel URL shows `{"status":"ok","message":"AI Google Slides Generator API",...}` because that’s the API root.

To get the **landing page** (prompt input, “Generate Presentation” button, result with link), deploy the **frontend** as a second project and use its URL as your main link.

---

## Steps (about 5 minutes)

### 1. Note your backend URL

Your backend is already live, e.g.:

- `https://ppt-agent.vercel.app`

Use that exact URL (no trailing slash) in step 4.

---

### 2. Create a second Vercel project for the frontend

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. **Import** the same Git repository you use for the backend (e.g. `ppt_agent`).
3. **Do not** deploy yet.

---

### 3. Set the root directory to the frontend

1. In the new project, open **Settings** → **General**.
2. Find **Root Directory**.
3. Click **Edit**, set it to **`ppt-agent-frontend`**, and save.

---

### 4. Add the backend URL as an environment variable

1. In the same project, go to **Settings** → **Environment Variables**.
2. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** your backend URL, e.g. `https://ppt-agent.vercel.app` (no trailing slash)
   - **Environment:** Production (and Preview if you use previews)
3. Save.

---

### 5. Deploy

1. Go to **Deployments**.
2. Trigger a new deployment (e.g. **Redeploy** the latest, or push a new commit).

---

### 6. Use the frontend URL as your main link

After the deployment finishes, the frontend project will have its own URL, e.g.:

- `https://ppt-agent-frontend.vercel.app`  
  or  
- `https://ppt-agent-frontend-&lt;your-team&gt;.vercel.app`

**Use this URL** when you want to open the app. There you’ll see:

- “AI-Powered Presentation Creation”
- Prompt textarea and “Generate Presentation”
- After generation: title, slide count, “View Presentation”, “Create Another”

The backend URL (e.g. `https://ppt-agent.vercel.app`) is still used by the frontend in the background for the API; you don’t need to open it directly.

---

## Optional: one main domain

- In the **frontend** project, go to **Settings** → **Domains** and add your main domain (e.g. `app.yourdomain.com`).
- Keep the backend on its default Vercel URL (or a subdomain like `api.yourdomain.com`) and keep `VITE_API_URL` pointing to that backend URL.

---

## Summary

| What you see now | What you want |
|------------------|----------------|
| One project → backend only → visiting the URL shows API JSON | Two projects: backend (API) + frontend (landing page). Use the **frontend** URL as the main link. |

After you deploy the frontend project and set `VITE_API_URL`, the “only deployed” situation is fixed: you’ll have both API and landing page, with the frontend as the main entry point.
