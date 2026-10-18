# IntelliDocs frontend (React + Vite)
npm install && npm run dev   # http://localhost:5173
Dev: /api/* is proxied to http://localhost:8000 (vite.config.js). Production: set VITE_API_URL (see .env.example)
and allow your frontend origin in FastAPI CORSMiddleware.
