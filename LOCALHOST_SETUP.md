# Localhost Deployment Guide

This guide will help you run the PPT Agent project on your local machine.

## Prerequisites

✅ **Already Installed:**
- Python 3.13.5
- Node.js v23.10.0
- npm 10.9.2
- Virtual environment created
- Python dependencies installed
- Frontend dependencies installed
- Google credentials file exists

## Quick Start

### Option 1: Use the Start Script (Recommended)

```bash
./start_servers.sh
```

This script will:
1. Build the frontend
2. Start the backend on port 8001
3. Optionally start the frontend dev server on port 5173

### Option 2: Manual Start

#### Start Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Backend will be available at:
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

#### Start Frontend (Development)

```bash
cd ppt-agent-frontend
npm run dev
```

Frontend will be available at:
- **Frontend**: http://localhost:5173

## Environment Variables

The project uses a `.env` file for configuration. Make sure you have:

- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `GOOGLE_CREDENTIALS_PATH` - Path to service account JSON (default: `credentials/service_account.json`)

The `.env` file already exists in your project.

## Access Points

Once running:

1. **Backend API**: http://localhost:8001
2. **API Documentation**: http://localhost:8001/docs (Interactive Swagger UI)
3. **Frontend Dev Server**: http://localhost:5173 (if started)
4. **Health Check**: http://localhost:8001/health

## Stopping Servers

### Using the stop script:
```bash
./stop_servers.sh
```

### Manually:
```bash
# Stop backend
pkill -9 -f "uvicorn.*ppt_agent"

# Stop frontend
pkill -9 -f "vite.*ppt-agent"
```

## Troubleshooting

### Backend won't start
- Check if port 8001 is already in use: `lsof -i :8001`
- Check logs: `/tmp/ppt_agent_server.log`
- Verify virtual environment is activated: `which python` should show `venv/bin/python`

### Frontend won't start
- Check if port 5173 is already in use: `lsof -i :5173`
- Check logs: `/tmp/ppt_agent_frontend.log`
- Reinstall dependencies: `cd ppt-agent-frontend && npm install`

### Missing API Keys
- Ensure `.env` file exists and contains `ANTHROPIC_API_KEY`
- Verify Google credentials file exists at `credentials/service_account.json`

## Development Tips

- Backend auto-reloads on code changes (thanks to `--reload` flag)
- Frontend dev server has hot module replacement
- Check `/tmp/ppt_agent_server.log` for backend logs
- Check `/tmp/ppt_agent_frontend.log` for frontend logs

## Next Steps

1. Open http://localhost:8001/docs to explore the API
2. Open http://localhost:5173 to use the frontend interface
3. Try generating a presentation!

