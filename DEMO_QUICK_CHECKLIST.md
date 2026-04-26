# QUICK DEMO CHECKLIST - Print This Out

## PRE-RECORDING CHECKLIST ✓

- [ ] PostgreSQL installed and running
- [ ] Project cloned from GitHub
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with PostgreSQL connection
- [ ] Database initialized (`python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"`)
- [ ] Have 3 terminals ready (or tabs)
- [ ] Screen recording software installed
- [ ] Read through DEMO_RECORDING_GUIDE.md

## DURING RECORDING - FOLLOW THIS SEQUENCE

### STEP 1: Start Backend (Terminal 1)
```bash
cd C:\Users\venka\Music\resume\data-pipeline-monitor
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```
**SAY:** "Backend API starting on port 8000"
**RECORD TIME:** 10 seconds

---

### STEP 2: Start Dashboard (Terminal 2)
```bash
cd C:\Users\venka\Music\resume\data-pipeline-monitor
venv\Scripts\activate
streamlit run frontend/app.py
```
**SAY:** "Streamlit dashboard starting on port 8501"
**RECORD TIME:** 10 seconds

---

### STEP 3: Check API Health (Browser)
```
URL: http://localhost:8000/health
```
**SAY:** "API is healthy and operational"
**RECORD TIME:** 5 seconds

---

### STEP 4: Show API Docs (Browser)
```
URL: http://localhost:8000/docs
```
**SAY:** "Complete REST API documentation with all endpoints"
**SCROLL:** Show metrics, anomalies, recommendations endpoints
**RECORD TIME:** 20 seconds

---

### STEP 5: Create Single Metric (Swagger)
**Endpoint:** POST /api/metrics/
**Click:** "Try it out"
**Use:**
```json
{
  "pipeline_name": "etl_pipeline",
  "metric_type": "latency",
  "value": 123.45
}
```
**SAY:** "Creating a metric for our ETL pipeline"
**RECORD TIME:** 20 seconds

---

### STEP 6: Create Batch Metrics (Swagger)
**Endpoint:** POST /api/metrics/batch
**Click:** "Try it out"
**Use:**
```json
[
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 100.0
  },
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 105.0
  },
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 102.0
  },
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 103.0
  },
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 101.0
  },
  {
    "pipeline_name": "etl_pipeline",
    "metric_type": "latency",
    "value": 500.0
  }
]
```
**SAY:** "Batch loading 6 metrics. The first 5 are normal, the last is an outlier"
**RECORD TIME:** 30 seconds

---

### STEP 7: Detect Anomalies (Swagger)
**Endpoint:** POST /api/anomalies/detect
**Parameters:**
- pipeline_name: `etl_pipeline`
- metric_type: `latency`
**SAY:** "Running anomaly detection... The system detected the 500ms spike as CRITICAL"
**SHOW:** Severity field and Z-score in response
**RECORD TIME:** 30 seconds

---

### STEP 8: Generate Recommendation (Swagger)
**Endpoint:** POST /api/recommendations/generate
**Parameter:** anomaly_id: `1`
**SAY:** "System generated a recommendation to implement caching with specific steps"
**RECORD TIME:** 30 seconds

---

### STEP 9: Open Dashboard (Browser)
```
URL: http://localhost:8501
```
**SAY:** "Now let's look at the real-time dashboard"
**RECORD TIME:** 5 seconds

---

### STEP 10: Overview Page (Dashboard)
**On:** Overview tab (default)
**SHOW:**
- System Status: operational
- Pipelines Monitored: 2
- Active Anomalies: 1
- Pending Recommendations: 1
**SAY:** "System overview shows instant health metrics"
**RECORD TIME:** 20 seconds

---

### STEP 11: Pipelines Page (Dashboard)
**Click:** "Pipelines" in sidebar
**Select:** "etl_pipeline"
**SHOW:**
- Status: WARNING
- Recent Anomaly
- Recommendation
**SAY:** "Pipeline-specific view with anomaly and recommendation details"
**EXPAND:** Anomaly and recommendation sections
**RECORD TIME:** 40 seconds

---

### STEP 12: Anomalies Page (Dashboard)
**Click:** "Anomalies" in sidebar
**SHOW:**
- Anomalies table
- Severity filter
- Our detected anomaly
**SAY:** "All anomalies in one place with filtering"
**RECORD TIME:** 20 seconds

---

### STEP 13: Recommendations Page (Dashboard)
**Click:** "Recommendations" in sidebar
**EXPAND:** Recommendation
**SHOW:**
- Title
- Description
- Implementation Steps
- Estimated Improvement
**SAY:** "Actionable recommendations with specific steps and estimated impact"
**RECORD TIME:** 30 seconds

---

### STEP 14: Run Tests (Terminal 3)
```bash
cd C:\Users\venka\Music\resume\data-pipeline-monitor
venv\Scripts\activate
pytest -v
```
**SHOW:** Tests running and passing
**SAY:** "50+ comprehensive tests, all passing"
**RECORD TIME:** 20 seconds

---

### STEP 15: Show Coverage (Terminal 3)
```bash
pytest --cov=backend --cov-report=term-missing
```
**SHOW:** Coverage percentage
**SAY:** "87% code coverage - production-grade quality"
**RECORD TIME:** 15 seconds

---

## TOTAL RECORDING TIME: ~10 minutes

## POST-RECORDING TASKS

- [ ] Save video file
- [ ] Edit video (add titles, transitions, music)
- [ ] Export as 1080p MP4
- [ ] Upload to LinkedIn
- [ ] Use provided LinkedIn caption
- [ ] Share with 50+ recruiters
- [ ] Post on GitHub issues

---

## WHAT TO SAY AT KEY MOMENTS

### When showing metrics ingestion:
"Metrics can come from anywhere - Prometheus, CloudWatch, Datadog. We support real-time ingestion."

### When showing anomaly:
"This is real anomaly detection, not just alerting. Statistical analysis catches the real problem."

### When showing recommendation:
"The system doesn't just tell you something is wrong - it tells you exactly how to fix it."

### When showing dashboard:
"This is where your ops team spends their day. One place to see everything."

### When showing tests:
"This isn't prototype code. 50+ tests, 87% coverage, production-ready."

---

## LINKEDIN VIDEO POST CAPTION

After you upload the video, use this caption:

---

Just recorded a demo of the data pipeline monitoring system I built.

What it does:
✅ Ingest metrics in real-time (single or batch)
✅ Automatically detect anomalies using statistical analysis
✅ Generate AI-powered optimization recommendations
✅ Beautiful real-time dashboard
✅ Complete REST API

This is exactly what Meta, Uber, Stripe, and every data-driven company needs.

Companies pay Datadog $1M+/year for this. I built it open source.

✨ Production-ready: 50+ tests, 87% coverage, Docker containerized
✨ Full-stack: FastAPI backend, Streamlit UI, PostgreSQL database
✨ Real value: Solves problems companies actually have

Watch the full demo in the video above 👆

GitHub: github.com/vsk7797/data-pipeline-monitor

Hiring for data/platform/ML infrastructure roles? Let's talk. This is what production engineering looks like.

#DataEngineering #Python #FastAPI #SoftwareEngineering #OpenSource #MachineLearning

---

## COMMON ISSUES & FIXES

### "PostgreSQL connection refused"
- Make sure PostgreSQL service is running
- Check connection string in .env

### "Port 8000 already in use"
- Use different port: `uvicorn backend.main:app --port 8001`

### "Tests fail"
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt --force-reinstall`

### "Dashboard won't load"
- Make sure backend is running
- Check API URL in Settings

### "No anomalies detected"
- Make sure you created 6 metrics with the 500ms outlier
- Run batch detection instead

---

## SUCCESS METRICS

After posting:
- ✅ 10+ views in first hour
- ✅ 20+ views in first day
- ✅ 5+ recruiter messages within 1 week
- ✅ 50+ recruiter messages within 2 weeks
- ✅ Interests from Meta, Uber, Stripe

Good luck! 🚀
