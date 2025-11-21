# 🎨 PPT Agent - AI-Powered Presentation Generator

Create stunning presentations with AI in seconds. Powered by Anthropic Claude and Google Slides API.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🤖 **AI-Powered Content Generation**: Uses Anthropic Claude API with tool calling for intelligent presentation creation
- 🎨 **Automatic Professional Design**: Beautiful slides with professional layouts automatically applied
- ⚡ **Fast Generation**: Create presentations in seconds, not hours
- 📊 **Customizable**: Specify topic, number of slides, and key points
- 🔗 **Direct Google Slides Integration**: Presentations are created directly in Google Slides
- 🚀 **Modern Web Interface**: Beautiful React frontend with shadcn/ui components
- 🛠️ **Autonomous AI Agent**: Agent makes decisions and uses tools to create complete presentations

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for frontend)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Google Cloud Project with Slides API and Drive API enabled
- Google Service Account credentials (JSON file)

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ppt-agent.git
cd ppt-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_CREDENTIALS_PATH`: Path to your Google service account JSON file
- `DEFAULT_PRESENTATION_ID`: Google Slides presentation ID to edit

5. **Run the backend:**
```bash
# Using the start script
./start_servers.sh

# Or manually
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

The API will be available at `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd ppt-agent-frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env if needed (defaults to http://localhost:8001)
```

4. **Run the frontend:**
```bash
npm run dev
```

Visit `http://localhost:5173` to see the interface.

### Using the Start Scripts

For convenience, use the provided scripts:

```bash
# Start both backend and frontend
./start_servers.sh

# Stop all servers
./stop_servers.sh
```

## 📦 Deployment

### Deploy to Vercel

#### Backend Deployment

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy:**
```bash
vercel --prod
```

4. **Set environment variables in Vercel dashboard:**
   - Go to your project settings
   - Navigate to Environment Variables
   - Add the following:
     - `ANTHROPIC_API_KEY`: Your Anthropic API key
     - `GOOGLE_CREDENTIALS_PATH`: Path to credentials (for serverless, you may need to base64 encode)
     - `DEFAULT_PRESENTATION_ID`: Your Google Slides presentation ID
     - `FRONTEND_URL`: Your frontend URL (for CORS)

#### Frontend Deployment

1. **Navigate to frontend:**
```bash
cd ppt-agent-frontend
```

2. **Update API URL:**
Create `.env.production`:
```env
VITE_API_URL=https://your-backend-url.vercel.app
```

3. **Deploy:**
```bash
vercel --prod
```

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Anthropic Claude API**: AI model for content generation with tool calling
- **Google Slides API**: Create and edit presentations
- **Google Drive API**: Manage file sharing and access
- **Uvicorn**: ASGI server for FastAPI
- **Mangum**: ASGI adapter for AWS Lambda/Vercel

### Frontend
- **React 19**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **shadcn/ui**: Beautiful, accessible UI components
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Axios**: HTTP client

## 📝 API Documentation

### Generate Presentation

**Endpoint:** `POST /generate-presentation`

**Request Body:**
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

**Error Response:**
```json
{
  "error": "Error message",
  "type": "ErrorType",
  "detail": "Detailed error information"
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

### API Documentation (Swagger)

Visit `http://localhost:8001/docs` for interactive API documentation.

## 🏗️ Project Structure

```
ppt_agent/
├── app/
│   ├── __init__.py
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
│   │   ├── main.tsx            # React entry point
│   │   ├── components/         # React components
│   │   ├── services/           # API service layer
│   │   └── lib/                # Utility functions
│   └── package.json
├── credentials/                # Google credentials (not in repo)
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel configuration
├── start_servers.sh            # Start script
├── stop_servers.sh             # Stop script
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `ANTHROPIC_API_KEY`: Required - Your Anthropic API key
- `GOOGLE_CREDENTIALS_PATH`: Required - Path to Google service account JSON
- `DEFAULT_PRESENTATION_ID`: Required - Google Slides presentation ID
- `GOOGLE_DRIVE_FOLDER_ID`: Optional - Google Drive folder ID
- `AGENT_MAX_ITERATIONS`: Optional - Maximum agent iterations (default: 20)
- `AGENT_MODEL`: Optional - Anthropic model to use (default: claude-3-haiku-20240307)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Sharath Kumar**

## 🙏 Acknowledgments

- [Anthropic Claude API](https://www.anthropic.com/) for AI capabilities
- [Google Slides API](https://developers.google.com/slides) for presentation creation
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ using AI
