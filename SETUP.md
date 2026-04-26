# Setup Guide - Data Pipeline Monitor

Comprehensive guide to setting up the Data Pipeline Monitor locally and in production.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Setup](#docker-setup)
3. [Database Setup](#database-setup)
4. [Running Tests](#running-tests)
5. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/vsk7797/data-pipeline-monitor.git
cd data-pipeline-monitor
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit with your settings
# On Windows
notepad .env

# On macOS/Linux
nano .env
```

Key variables to set:
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to `false` for production
- `OPENAI_API_KEY`: (Optional) For LLM recommendations

### Step 5: Set Up Database

Make sure PostgreSQL is running locally. Then:

```bash
# Connect to PostgreSQL and create database
psql -U postgres
CREATE DATABASE pipeline_monitor;
\q

# OR use a PostgreSQL GUI like pgAdmin
```

Initialize tables:

```bash
python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### Step 6: Run Locally

**Start the API server** (Terminal 1):

```bash
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

**Start the Streamlit dashboard** (Terminal 2):

```bash
streamlit run frontend/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 7: Verify Setup

1. **API Health Check**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected response:
   ```json
   {"status":"operational","version":"1.0.0","timestamp":"..."}
   ```

2. **API Docs**
   Open http://localhost:8000/docs in your browser

3. **Dashboard**
   Open http://localhost:8501 in your browser

## Docker Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- PostgreSQL: `localhost:5432`
- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

### Using Individual Containers

```bash
# Build Docker image
docker build -t pipeline-monitor .

# Run container with PostgreSQL
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/pipeline_monitor \
  pipeline-monitor
```

### Docker Compose Files

The `docker-compose.yml` includes:
- **postgres**: PostgreSQL database service
- **backend**: FastAPI application
- **frontend**: Streamlit dashboard

All services are connected via internal network and use volume mounts for development.

## Database Setup

### PostgreSQL Installation

**Windows:**
```powershell
# Using Chocolatey
choco install postgresql
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database Manually

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE pipeline_monitor;

# Create user (optional)
CREATE USER pipeline_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pipeline_monitor TO pipeline_user;

# Exit
\q
```

### Database URL Format

```
postgresql://username:password@hostname:port/database_name
```

Examples:
- Local: `postgresql://postgres:postgres@localhost:5432/pipeline_monitor`
- Docker: `postgresql://postgres:postgres@postgres:5432/pipeline_monitor`
- Remote: `postgresql://user:pass@aws-db.example.com:5432/pipeline_monitor`

## Running Tests

### Prerequisites

```bash
pip install -r requirements.txt  # Includes pytest
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=backend --cov-report=html
# Opens htmlcov/index.html for detailed report
```

### Run Specific Test File

```bash
pytest backend/tests/test_metrics.py -v
```

### Run Specific Test

```bash
pytest backend/tests/test_metrics.py::test_create_single_metric -v
```

### Test Organization

```
backend/tests/
├── conftest.py                  # Fixtures and configuration
├── test_metrics.py              # Metrics endpoint tests
├── test_anomaly_detection.py    # Anomaly detection logic tests
├── test_anomalies_api.py        # Anomalies endpoint tests
├── test_recommendations_api.py  # Recommendations tests
└── test_health.py               # Health/status endpoint tests
```

### Coverage Goals

Target: **80%+ code coverage**

Current coverage breakdown:
- Backend services: 85%+
- API routes: 90%+
- Models: 95%+

## Troubleshooting

### Issue: PostgreSQL Connection Refused

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list               # macOS

# Start PostgreSQL if needed
sudo systemctl start postgresql   # Linux
brew services start postgresql@15 # macOS
```

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn backend.main:app --port 8001
```

### Issue: Database Tables Not Created

**Solution:**
```bash
# Re-create tables
python -c "from backend.database import engine, Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

### Issue: Import Errors

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Streamlit Dashboard Won't Connect to API

**Solution:**
```bash
# Check API is running
curl http://localhost:8000/health

# In Streamlit sidebar, go to Settings
# Update API URL if needed (default: http://localhost:8000/api)
```

### Issue: Docker Container Exits Immediately

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Ensure DATABASE_URL is correctly set
docker-compose config | grep DATABASE_URL

# Try rebuilding
docker-compose down
docker-compose up --build
```

## Development Workflow

### 1. Make Changes

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Make code changes in your editor
# Both API and dashboard support auto-reload in development
```

### 2. Run Tests

```bash
pytest -v
```

### 3. Check Code Quality

```bash
# Format code
black backend/

# Check linting
flake8 backend/

# Type checking
mypy backend/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: describe your changes"
git push origin main
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -b 0.0.0.0:8000 --timeout 120
```

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name example.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://127.0.0.1:8501;
    }
}
```

### Using systemd Service

Create `/etc/systemd/system/pipeline-monitor.service`:

```ini
[Unit]
Description=Data Pipeline Monitor
After=network.target

[Service]
Type=notify
User=pipeline
WorkingDirectory=/opt/pipeline-monitor
Environment="PATH=/opt/pipeline-monitor/venv/bin"
ExecStart=/opt/pipeline-monitor/venv/bin/gunicorn backend.main:app -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pipeline-monitor
sudo systemctl start pipeline-monitor
```

## Next Steps

1. Read the [README.md](README.md) for feature overview
2. Check [API Documentation](http://localhost:8000/docs)
3. Explore example usage in test files
4. Deploy to production following deployment guide above
