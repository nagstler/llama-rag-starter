# Sales Agent Chat UI

A modern, production-ready chat interface for the Sales Operations Agent built with Next.js and TypeScript.

## Features

- 🚀 Real-time streaming responses
- 🧠 Visual agent reasoning display
- 💬 Professional chat interface
- 🎨 Responsive design with Tailwind CSS
- ⚡ Server-side event streaming (SSE)
- 🔄 Automatic API proxying

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

## Installation

```bash
# From the frontend directory
npm install
# or
yarn install
```

## Development

```bash
# Start the development server
npm run dev
# or
yarn dev
```

The app will be available at http://localhost:3000

## Production Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Architecture

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Server-Side Events** - Real-time streaming

## API Integration

The frontend automatically proxies API requests to the backend:
- `/api/*` → `http://localhost:8000/*`

This is configured in `next.config.js` for development.

## Key Components

### Chat Interface (`app/page.tsx`)
- Message display with user/assistant distinction
- Real-time streaming of responses
- Agent reasoning visualization
- Example questions sidebar

### Streaming Handler
- Parses SSE stream from backend
- Handles reasoning steps and content chunks
- Error handling and recovery

## Environment Variables

Create a `.env.local` file for any frontend-specific configuration:

```env
# Optional: Override backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Vercel (Recommended)
```bash
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Customization

### Styling
- Modify `app/globals.css` for global styles
- Update Tailwind config in `tailwind.config.js`

### Agent Configuration
- Update reasoning step icons in `getStepIcon()`
- Customize assistant avatar and name
- Modify sidebar example questions

## Troubleshooting

### "Cannot connect to API"
- Ensure backend is running on port 8000
- Check CORS settings in backend

### Streaming not working
- Verify SSE endpoint is working: `curl http://localhost:8000/agent/chat/stream`
- Check browser console for errors

### Build errors
- Clear `.next` folder and rebuild
- Ensure all dependencies are installed