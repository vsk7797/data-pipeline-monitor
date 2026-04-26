# Data Pipeline Monitor

Real-time monitoring and optimization system for data pipelines using AI-powered anomaly detection and intelligent recommendations.

## 🎯 Features

- **Real-time Metrics Ingestion**: Accept pipeline metrics from multiple sources
- **AI-Powered Anomaly Detection**: Detect performance issues using statistical analysis
- **Intelligent Recommendations**: Get AI-generated optimization suggestions
- **Interactive Dashboard**: Beautiful Streamlit UI for monitoring and analytics
- **RESTful API**: Complete API for programmatic access
- **Production-Ready**: Docker support, comprehensive tests, error handling
- **Scalable Architecture**: Designed for high-volume metrics ingestion

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vsk7797/data-pipeline-monitor.git
cd data-pipeline-monitor
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
# Make sure PostgreSQL is running
python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### Running with Docker

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- Streamlit frontend on port 8501

### Manual Development Setup

**Terminal 1 - Start Backend API:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Start Frontend Dashboard:**
```bash
streamlit run frontend/app.py
```

## 📊 API Endpoints

### Metrics
- `POST /api/metrics/` - Create a single metric
- `POST /api/metrics/batch` - Create multiple metrics
- `GET /api/metrics/` - Get metrics (with filtering)
- `GET /api/metrics/pipeline/{name}` - Get all metrics for a pipeline
- `GET /api/metrics/{id}` - Get specific metric

### Anomalies
- `GET /api/anomalies/` - Get anomalies (with filtering)
- `POST /api/anomalies/detect` - Detect anomalies for a metric
- `POST /api/anomalies/batch-detect` - Detect anomalies across all pipelines
- `PATCH /api/anomalies/{id}/resolve` - Mark anomaly as resolved

### Recommendations
- `GET /api/recommendations/` - Get recommendations
- `POST /api/recommendations/generate` - Generate recommendation for anomaly
- `POST /api/recommendations/batch-generate` - Generate recommendations batch
- `PATCH /api/recommendations/{id}/implement` - Mark as implemented

### Health & Status
- `GET /health` - System health check
- `GET /api/system-health` - Detailed system status
- `GET /api/pipelines` - List all monitored pipelines
- `GET /api/pipelines/{name}` - Get pipeline health

## 📈 Usage Examples

### Ingest Metrics

```bash
# Single metric
curl -X POST "http://localhost:8000/api/metrics/" \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 123.45,
    "metadata": {"stage": "transform"}
  }'

# Batch metrics
curl -X POST "http://localhost:8000/api/metrics/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "pipeline_name": "etl_pipeline",
      "metric_type": "latency",
      "value": 100.0
    },
    {
      "pipeline_name": "ml_pipeline",
      "metric_type": "error_rate",
      "value": 0.02
    }
  ]'
```

### Detect Anomalies

```bash
# Detect for specific metric
curl -X POST "http://localhost:8000/api/anomalies/detect?pipeline_name=etl_pipeline&metric_type=latency"

# Batch detection (all pipelines)
curl -X POST "http://localhost:8000/api/anomalies/batch-detect"
```

### Generate Recommendations

```bash
# For specific anomaly
curl -X POST "http://localhost:8000/api/recommendations/generate?anomaly_id=1"

# Batch generation
curl -X POST "http://localhost:8000/api/recommendations/batch-generate"
```

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage report
pytest --cov=backend --cov-report=html

# Specific test file
pytest backend/tests/test_metrics.py -v

# Specific test
pytest backend/tests/test_metrics.py::test_create_single_metric -v
```

## 📁 Project Structure

```
data-pipeline-monitor/
├── backend/
│   ├── models/
│   │   ├── __init__.py          # Database models
│   │   └── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── metrics.py           # Metrics endpoints
│   │   ├── anomalies.py         # Anomaly endpoints
│   │   ├── recommendations.py   # Recommendation endpoints
│   │   └── health.py            # Health endpoints
│   ├── services/
│   │   ├── anomaly_detector.py  # Anomaly detection logic
│   │   └── optimizer.py         # Recommendation engine
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── test_metrics.py
│   │   ├── test_anomaly_detection.py
│   │   ├── test_anomalies_api.py
│   │   ├── test_recommendations_api.py
│   │   └── test_health.py
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Configuration
│   ├── database.py              # Database setup
│   └── __init__.py
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── Dockerfile                   # Backend container
├── Dockerfile.streamlit         # Frontend container
├── docker-compose.yml           # Multi-container setup
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Environment template
├── .gitignore
└── README.md
```

## 🔧 Configuration

Edit `.env` file to configure:

```
DATABASE_URL=postgresql://user:password@localhost:5432/pipeline_monitor
DEBUG=false
API_PORT=8000
OPENAI_API_KEY=your_key_here
ANOMALY_THRESHOLD=0.8
CHECK_INTERVAL_SECONDS=300
```

## 🏗️ Architecture

### Metrics Flow
```
Metric Input → Ingestion API → PostgreSQL → Anomaly Detection → Recommendations
                                                  ↓
                                            Streamlit Dashboard
```

### Anomaly Detection
- **Statistical Analysis**: Z-score based outlier detection
- **Trend Analysis**: Sustained change detection
- **Severity Classification**: Critical, High, Medium, Low

### Recommendation Engine
- **Heuristic-based**: Pattern matching with curated recommendations
- **LLM Integration**: (Optional) OpenAI integration for advanced suggestions
- **Impact Assessment**: High/Medium/Low impact rating

## 📊 Monitoring Metrics

Supported metric types:
- `latency` - Pipeline execution time
- `throughput` - Records processed per time unit
- `error_rate` - Percentage of failed operations
- `memory_usage` - Resource consumption
- `cpu_usage` - Processor utilization

## 🔐 Security

- CORS middleware for cross-origin requests
- Trusted host validation
- SQL injection prevention via SQLAlchemy ORM
- Environment-based sensitive data management

## 📝 API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

Contributions welcome! Please ensure:
- All tests pass: `pytest`
- Code style: Black formatted
- Type hints included
- Docstrings for all functions

## 📄 License

MIT License - See LICENSE file for details

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**
```bash
export DATABASE_URL=postgresql://...
export OPENAI_API_KEY=sk-...
export DEBUG=false
```

2. **Run with Gunicorn**
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -b 0.0.0.0:8000
```

3. **Using Docker**
```bash
docker build -t pipeline-monitor .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  pipeline-monitor
```

## 📞 Support

For issues or questions:
- Check existing issues on GitHub
- Review API documentation at `/docs`
- Check test files for usage examples

## 🎉 Success Metrics

This project demonstrates:
- ✅ Full-stack development (API + UI + Database)
- ✅ Production-ready code (tests, docs, error handling)
- ✅ Real business value (solves actual company problems)
- ✅ Scalability thinking (handles real-time data)
- ✅ AI/ML integration (anomaly detection)
- ✅ DevOps knowledge (Docker, monitoring)
- ✅ System design (architecture, trade-offs)
