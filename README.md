# Neon-Linde RAG Chatbot

## Quick Start

### Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd neon-linde
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

### Stopping the application

```bash
docker-compose down
```

### Rebuilding after changes

```bash
docker-compose up --build
```

## Project Structure

```
neon-linde/
├── backend/              # Django backend
│   ├── chat/            # Chat application
│   ├── config/          # Django settings
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   ├── Dockerfile      # Frontend container
│   └── package.json    # Node dependencies
├── docker-compose.yml  # Docker orchestration
├── .env.example        # Environment template
└── .gitignore         # Git ignore rules
```

## Environment Variables

See `.env.example` for all available configuration options.

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Change `DJANGO_SECRET_KEY` to a secure random value
3. Update `POSTGRES_PASSWORD` to a strong password
4. Configure `AI_AGENT_URL` to your actual AI service
5. Set `MOCK_AI_RESPONSE=False` when using real AI service

## Troubleshooting

### Database connection issues
```bash
docker-compose down -v
docker-compose up --build
```

### Frontend not updating
Clear the browser cache or use incognito mode.

### Permission errors
Ensure Docker has proper permissions on your system.
