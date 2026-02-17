# PPT Agent - AI-Powered Presentation Generator

An autonomous AI agent that automates repetitive PowerPoint editing tasks, creating and managing presentations through intelligent automation. Built with Anthropic Claude API and Google Slides.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/sharathkum05/ppt_agent)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-blue.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

PPT Agent eliminates the manual, repetitive work involved in creating and editing presentations. Instead of spending hours formatting slides, structuring content, and managing multiple iterations, the AI agent handles these tasks autonomously.

The agent intelligently:
- Plans presentation structure based on your requirements
- Creates and formats slides automatically
- Manages content placement and styling
- Handles multiple editing iterations
- Finalizes and shares presentations

## Key Features

- **Autonomous AI Agent**: Makes independent decisions and executes presentation creation workflows
- **Tool Calling Architecture**: Uses Anthropic Claude's tool use API for structured operations
- **Automated Content Generation**: Generates structured content based on natural language prompts
- **Professional Layout Management**: Automatically applies consistent formatting and design
- **Iterative Refinement**: Reviews and improves slides before finalization
- **Google Slides Integration**: Direct creation and editing within Google Slides
- **Modern Web Interface**: React-based frontend with TypeScript and Tailwind CSS

## Technology Stack

**Backend**
- FastAPI - Modern async web framework
- Anthropic Claude API - AI agent with tool calling
- Google Slides API - Presentation creation and editing
- Google Drive API - File management and sharing
- Mangum - Serverless deployment adapter

**Frontend**
- React 19 with TypeScript
- Vite - Build tool and dev server
- shadcn/ui - UI component library
- Tailwind CSS - Utility-first styling
- Framer Motion - Animations

## Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for frontend development)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Google Cloud Project with Slides API and Drive API enabled
- Google Service Account credentials (JSON file)

## Quick Start

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/sharathkum05/ppt_agent.git
cd ppt_agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Run the backend:**
```bash
./start_servers.sh
# Or manually: uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd ppt-agent-frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**
```bash
cp .env.example .env
```

4. **Run the frontend:**
```bash
npm run dev
```

Visit `http://localhost:5173` to access the interface.

## Configuration

### Environment Variables

See `.env.example` for all configuration options:

**Required:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `GOOGLE_CREDENTIALS_PATH` - Path to Google service account JSON file
- `DEFAULT_PRESENTATION_ID` - Google Slides presentation ID to edit

**Optional:**
- `GOOGLE_DRIVE_FOLDER_ID` - Google Drive folder ID
- `AGENT_MAX_ITERATIONS` - Maximum agent iterations (default: 20)
- `AGENT_MODEL` - Anthropic model to use (default: claude-3-haiku-20240307)
- `AGENT_ENABLE_REVIEW` - Enable agent review step (default: true)

## API Documentation

### Generate Presentation

**Endpoint:** `POST /generate-presentation`

**Request:**
```json
{
  "prompt": "Create a 5-slide presentation about renewable energy, covering solar, wind, hydro, benefits, and future outlook"
}
```

**Response:**
```json
{
  "presentation_id": "1ssIEyRV9ARbPZcKoUcl1sneIlUsW_p-ipRl7KnRRCDk",
  "shareable_link": "https://docs.google.com/presentation/d/1ssIEyRV9ARbPZcKoUcl1sneIlUsW_p-ipRl7KnRRCDk/edit",
  "title": "Renewable Energy",
  "slide_count": 5
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "services": "initialized",
  "agent": "ready"
}
```

Interactive API documentation available at `http://localhost:8001/docs` when running locally.

## Project Structure

```
ppt_agent/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── agent/
│   │   ├── executor.py         # Tool executor for AI agent
│   │   └── tools.py            # Available tools for agent
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── agent_service.py    # AI agent service
│   │   ├── slides_service.py   # Google Slides API service
│   │   ├── drive_service.py    # Google Drive API service
│   │   └── llm_service.py      # LLM service
│   └── utils/
│       ├── auth.py             # Google authentication
│       └── anthropic_safe.py   # Safe Anthropic API wrapper
├── ppt-agent-frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx             # Main React component
│   │   ├── components/         # React components
│   │   └── services/           # API service layer
│   └── package.json
├── credentials/                # Google credentials (not in repo)
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Deployment

### Deploy to Vercel

**Backend** (from repo root; this is what’s deployed if you only ran `vercel` once):
```bash
vercel --prod
```
→ Visiting the project URL shows the API (e.g. `{"status":"ok",...}`).

**Frontend** (landing page with prompt + “Generate Presentation”):
- Deploy from the **ppt-agent-frontend** folder as a **separate Vercel project** (same repo, Root Directory = `ppt-agent-frontend`), and set `VITE_API_URL` to your backend URL.
- Step-by-step: see **[DEPLOY_FRONTEND.md](./DEPLOY_FRONTEND.md)**.

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Environment Variables for Vercel

Configure these in your Vercel project settings:
- `ANTHROPIC_API_KEY`
- `GOOGLE_CREDENTIALS_JSON` (base64 encoded service account JSON)
- `DEFAULT_PRESENTATION_ID`
- `GOOGLE_DRIVE_FOLDER_ID`
- `FRONTEND_URL` (set after frontend deployment)

## How It Works

1. **User Input**: Provide a natural language prompt describing the presentation
2. **Agent Planning**: AI agent analyzes requirements and plans structure
3. **Tool Execution**: Agent uses available tools (create_slide, add_content, format_slide)
4. **Iterative Refinement**: Agent reviews and improves slides automatically
5. **Finalization**: Agent finalizes presentation and generates shareable link

The agent handles all repetitive tasks including formatting, content structuring, slide organization, and presentation management.

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Sharath Kumar**

## Acknowledgments

- [Anthropic Claude API](https://www.anthropic.com/) for AI capabilities
- [Google Slides API](https://developers.google.com/slides) for presentation creation
- [shadcn/ui](https://ui.shadcn.com/) for UI components
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/sharathkum05/ppt_agent/issues).
