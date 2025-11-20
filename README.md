# AI Google Slides Generator

An **autonomous AI agent** that creates Google Slides presentations from a single prompt using Anthropic Claude API with tool calling and Google Slides API.

## Features

- 🤖 **True AI Agent**: Uses Anthropic's tool use API for autonomous decision-making
- 🛠️ **Tool Calling**: Agent can call functions (create_presentation, add_slide, review, refine, finalize)
- 🔄 **Iterative Refinement**: Agent can review and improve slides before finalizing
- 📊 **Intelligent Planning**: Agent reasons about presentation structure before creating
- 🚀 **Autonomous Workflow**: Agent manages the entire presentation creation process
- 🔗 **Auto-sharing**: Automatically shares presentations with shareable links
- ⚡ **FastAPI Backend**: Modern async API framework

## Prerequisites

- Python 3.10 or higher
- Google Cloud Project with Slides API and Drive API enabled
- Google Service Account credentials (JSON file)
- Anthropic API key

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy `env.txt` to `.env`:
   ```bash
   cp env.txt .env
   ```

2. Edit `.env` and add your credentials:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_CREDENTIALS_PATH=credentials/service_account.json
   AGENT_MAX_ITERATIONS=20
   AGENT_ENABLE_REVIEW=true
   AGENT_MODEL=claude-3-5-sonnet-20241022
   ```

### 3. Setup Google Credentials

1. Place your Google service account JSON credentials file in the `credentials/` directory
2. Name it `service_account.json` (or update `GOOGLE_CREDENTIALS_PATH` in `.env`)

### 4. Enable Google APIs

Make sure the following APIs are enabled in your Google Cloud Project:
- Google Slides API
- Google Drive API

### 5. Grant Permissions

Your service account email needs permission to create and share presentations. You may need to:
- Share a folder in Google Drive with your service account email (if organizing presentations)
- Or ensure the service account has appropriate permissions in your workspace

## Running the Application

### Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Usage

### Generate Presentation

**Endpoint:** `POST /generate-presentation`

**Request Body:**
```json
{
  "prompt": "Create a presentation about artificial intelligence and machine learning"
}
```

**Response:**
```json
{
  "presentation_id": "1abc123...",
  "shareable_link": "https://docs.google.com/presentation/d/1abc123...",
  "title": "Artificial Intelligence and Machine Learning",
  "slide_count": 8
}
```

### Example using curl:

```bash
curl -X POST "http://localhost:8000/generate-presentation" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Introduction to Python programming for beginners"}'
```

### Example using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-presentation",
    json={"prompt": "Introduction to Python programming for beginners"}
)

data = response.json()
print(f"Presentation created: {data['shareable_link']}")
```

## AI Agent Architecture

This project implements a **true AI agent** using Anthropic's tool use API. Unlike simple LLM integration, the agent can:

### How It Works

1. **User sends prompt** → "Create a presentation about AI"
2. **Agent reasons** → Plans the presentation structure
3. **Agent uses tools** → Calls functions autonomously:
   - `create_presentation(title)` - Creates new presentation
   - `add_slide(layout, title, content)` - Adds slides one by one
   - `review_presentation()` - Reviews current state
   - `refine_slide(slide_id, changes)` - Improves slides
   - `finalize_presentation()` - Shares and completes
4. **Agent iterates** → Can refine and improve
5. **Agent completes** → Returns final result

### Agent Workflow Example

```
User: "Create a presentation about Python"
  ↓
Agent: "I'll create a comprehensive presentation about Python programming"
  ↓
Agent calls: create_presentation("Introduction to Python")
  ↓
Agent: "Now I'll add slides covering key topics"
  ↓
Agent calls: add_slide("TITLE", "Introduction to Python", "...")
Agent calls: add_slide("TITLE_AND_BODY", "What is Python?", "...")
Agent calls: add_slide("TITLE_AND_BODY", "Python Features", "...")
  ↓
Agent calls: review_presentation()
  ↓
Agent: "The presentation looks good, but I should refine slide 2"
  ↓
Agent calls: refine_slide(2, "Better content...")
  ↓
Agent calls: finalize_presentation()
  ↓
Done! Returns shareable link
```

### Key Components

- **Agent Service** (`app/services/agent_service.py`): Main agent loop with Anthropic tool use
- **Tool Executor** (`app/agent/executor.py`): Executes tool calls and manages state
- **Tool Definitions** (`app/agent/tools.py`): Defines available tools for the agent
- **Enhanced Slides Service**: Granular methods for agent tool calls

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /generate-presentation` - Generate a new presentation from a prompt (uses AI agent)

## Project Structure

```
ppt_agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── tools.py            # Tool definitions for agent
│   │   └── executor.py        # Tool executor and state management
│   ├── services/
│   │   ├── agent_service.py    # AI Agent service with tool use
│   │   ├── llm_service.py      # Simple LLM service (legacy)
│   │   ├── slides_service.py   # Google Slides API
│   │   └── drive_service.py    # Google Drive API
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── utils/
│       └── auth.py             # Google authentication
├── credentials/
│   └── service_account.json    # Your Google credentials (not in repo)
├── env.txt                     # Environment variables template
├── .env                        # Your environment variables (not in repo)
├── requirements.txt
└── README.md
```

## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid input (e.g., empty prompt)
- **502 Bad Gateway**: External API errors (Google API, Anthropic API)
- **500 Internal Server Error**: Unexpected errors
- **503 Service Unavailable**: Services not initialized

## Troubleshooting

### Service Account Credentials Not Found
- Ensure `service_account.json` is in the `credentials/` directory
- Or update `GOOGLE_CREDENTIALS_PATH` in `.env`

### API Key Not Set
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Check that `.env` file exists and is in the project root

### Google API Errors
- Verify Google APIs are enabled in your Google Cloud Project
- Check service account has necessary permissions
- Ensure credentials JSON is valid

### Anthropic API Errors
- Verify your API key is valid
- Check your API usage limits
- Ensure you have sufficient credits

## License

This project is provided as-is for educational and development purposes.

