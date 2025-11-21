# PPT Agent Frontend

Modern, professional web interface for the PPT Agent using React, shadcn/ui, and Tailwind CSS.

## Features

- 🎨 Beautiful, modern UI with shadcn/ui components
- ⚡ Fast and responsive design
- 🎭 Smooth animations with Framer Motion
- 📱 Fully responsive (mobile, tablet, desktop)
- 🎯 Intuitive user experience
- 🔔 Toast notifications for feedback

## Tech Stack

- **React 18+** with TypeScript
- **Vite** for fast development and building
- **shadcn/ui** for beautiful components
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Axios** for API calls
- **Lucide React** for icons

## Development

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8001
```

## Integration with Backend

The frontend is configured to work with the FastAPI backend. After building:

1. Build the frontend: `npm run build`
2. The backend will serve the frontend from `ppt-agent-frontend/dist/`
3. Access the app at `http://localhost:8001`

## Project Structure

```
src/
  ├── components/
  │   └── ui/          # shadcn/ui components
  ├── services/
  │   └── api.ts       # API integration
  ├── App.tsx          # Main app component
  ├── main.tsx        # Entry point
  └── index.css        # Global styles
```

## Usage

1. Enter a prompt describing your presentation
2. Click "Generate Presentation"
3. Wait for the AI to create your slides
4. Open the presentation in Google Slides or copy the link
