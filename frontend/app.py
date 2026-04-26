"""Streamlit dashboard for Data Pipeline Monitor"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Data Pipeline Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .critical { color: #ff0000; }
    .high { color: #ff6b00; }
    .medium { color: #ffd700; }
    .low { color: #00d700; }
    </style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = st.secrets.get("api_url", "http://localhost:8000/api")

@st.cache_data(ttl=300)
def get_system_health():
    """Fetch system health from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/system-health", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error fetching system health: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_all_pipelines():
    """Fetch all monitored pipelines"""
    try:
        response = requests.get(f"{API_BASE_URL}/pipelines", timeout=5)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching pipelines: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_pipeline_health(pipeline_name):
    """Fetch health for a specific pipeline"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/pipelines/{pipeline_name}",
            timeout=5
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error fetching pipeline health: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_anomalies(pipeline_name=None, resolved=False):
    """Fetch anomalies"""
    try:
        params = {"resolved": resolved}
        if pipeline_name:
            params["pipeline_name"] = pipeline_name

        response = requests.get(f"{API_BASE_URL}/anomalies", params=params, timeout=5)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching anomalies: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_recommendations(pipeline_name=None, implemented=False):
    """Fetch recommendations"""
    try:
        params = {"implemented": implemented}
        if pipeline_name:
            params["pipeline_name"] = pipeline_name

        response = requests.get(
            f"{API_BASE_URL}/recommendations",
            params=params,
            timeout=5
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return []

def render_severity_badge(severity):
    """Render severity badge with color"""
    colors = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }
    return f"{colors.get(severity, '⚪')} {severity.upper()}"

# Main layout
st.title("📊 Data Pipeline Monitor")
st.markdown("Real-time monitoring and optimization for data pipelines")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select View",
    ["Overview", "Pipelines", "Anomalies", "Recommendations", "Settings"]
)

# Overview Page
if page == "Overview":
    st.header("System Overview")

    health = get_system_health()

    if health:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "System Status",
                health["status"].upper(),
                delta="All systems operational" if health["status"] == "operational" else "Issues detected",
            )

        with col2:
            st.metric(
                "Pipelines Monitored",
                health["pipelines_monitored"],
            )

        with col3:
            st.metric(
                "Active Anomalies",
                health["active_anomalies"],
                delta_color="inverse" if health["active_anomalies"] > 0 else "off",
            )

        with col4:
            st.metric(
                "Pending Recommendations",
                health["pending_recommendations"],
            )

        st.divider()

        # Anomalies by severity
        st.subheader("Anomalies by Severity")
        anomalies = get_anomalies()

        if anomalies:
            severity_counts = {}
            for anomaly in anomalies:
                severity = anomaly.get("severity", "low")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            col1, col2 = st.columns([1, 2])

            with col1:
                st.write("### Count")
                for severity, count in sorted(severity_counts.items()):
                    st.write(f"{render_severity_badge(severity)}: {count}")

            with col2:
                fig = px.pie(
                    values=list(severity_counts.values()),
                    names=[s.capitalize() for s in severity_counts.keys()],
                    title="Anomaly Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No active anomalies detected!")

# Pipelines Page
elif page == "Pipelines":
    st.header("Pipeline Status")

    pipelines = get_all_pipelines()

    if pipelines:
        selected_pipeline = st.selectbox("Select Pipeline", pipelines)

        if selected_pipeline:
            health = get_pipeline_health(selected_pipeline)

            if health:
                col1, col2, col3 = st.columns(3)

                with col1:
                    status_emoji = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "warning" else "🔴"
                    st.metric("Status", f"{status_emoji} {health['status'].upper()}")

                with col2:
                    st.metric("Metrics Collected", health["metrics_count"])

                with col3:
                    st.metric("Active Anomalies", health["anomalies_count"])

                st.divider()

                # Recent anomalies
                st.subheader("Recent Anomalies")
                if health["recent_anomalies"]:
                    for anomaly in health["recent_anomalies"]:
                        with st.expander(f"{render_severity_badge(anomaly['severity'])} {anomaly['metric_type']}"):
                            st.write(f"**Description:** {anomaly['description']}")
                            st.write(f"**Detected:** {anomaly['detected_at']}")
                            st.write(f"**Resolved:** {'✅ Yes' if anomaly['resolved'] else '❌ No'}")
                else:
                    st.success("No active anomalies for this pipeline")

                # Active recommendations
                st.subheader("Optimization Recommendations")
                if health["active_recommendations"]:
                    for rec in health["active_recommendations"]:
                        with st.expander(f"💡 {rec['title']}"):
                            st.write(f"**Description:** {rec['description']}")
                            st.write(f"**Impact:** {rec['impact']}")
                            st.write(f"**Estimated Improvement:** {rec['estimated_improvement']}")
                            st.write("**Steps:**")
                            for i, step in enumerate(rec['implementation_steps'], 1):
                                st.write(f"{i}. {step}")
                else:
                    st.info("No pending recommendations for this pipeline")
    else:
        st.info("No pipelines are being monitored yet. Start by ingesting metrics!")

# Anomalies Page
elif page == "Anomalies":
    st.header("Anomaly Detection")

    col1, col2 = st.columns(2)

    with col1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            ["critical", "high", "medium", "low"],
            default=["critical", "high"]
        )

    with col2:
        show_resolved = st.checkbox("Show Resolved Anomalies", value=False)

    anomalies = get_anomalies(resolved=show_resolved)

    if severity_filter:
        anomalies = [a for a in anomalies if a["severity"] in severity_filter]

    if anomalies:
        df = pd.DataFrame(anomalies)
        st.dataframe(
            df[["pipeline_name", "metric_type", "severity", "description", "detected_at"]],
            use_container_width=True,
        )

        st.subheader("Anomaly Details")
        selected_idx = st.selectbox("Select anomaly", range(len(anomalies)))
        if selected_idx is not None:
            anomaly = anomalies[selected_idx]
            st.json(anomaly)
    else:
        st.info("No anomalies matching the filter criteria")

# Recommendations Page
elif page == "Recommendations":
    st.header("Optimization Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        impact_filter = st.multiselect(
            "Filter by Impact",
            ["High", "Medium", "Low"],
            default=["High", "Medium"]
        )

    with col2:
        show_implemented = st.checkbox("Show Implemented", value=False)

    recommendations = get_recommendations(implemented=show_implemented)

    if impact_filter:
        recommendations = [r for r in recommendations if r["impact"] in impact_filter]

    if recommendations:
        for rec in recommendations:
            with st.expander(f"{rec['impact']} Impact - {rec['title']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Pipeline:** {rec['pipeline_name']}")
                    st.write(f"**Impact:** {rec['impact']}")

                with col2:
                    st.write(f"**Estimated Improvement:** {rec['estimated_improvement']}")
                    st.write(f"**Implemented:** {'✅' if rec['implemented'] else '❌'}")

                st.write(f"**Description:** {rec['description']}")

                st.write("**Implementation Steps:**")
                for i, step in enumerate(rec['implementation_steps'], 1):
                    st.write(f"{i}. {step}")
    else:
        st.info("No recommendations available")

# Settings Page
elif page == "Settings":
    st.header("Settings")

    st.subheader("API Configuration")
    api_url = st.text_input("API Base URL", value=API_BASE_URL)

    st.subheader("Manual Actions")

    if st.button("🔄 Refresh Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared!")

    if st.button("🔍 Run Batch Anomaly Detection", use_container_width=True):
        try:
            response = requests.post(f"{API_BASE_URL}/anomalies/batch-detect", timeout=10)
            if response.status_code == 200:
                anomalies = response.json()
                st.success(f"Detected {len(anomalies)} anomalies")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("💡 Generate Batch Recommendations", use_container_width=True):
        try:
            response = requests.post(
                f"{API_BASE_URL}/recommendations/batch-generate",
                timeout=10
            )
            if response.status_code == 200:
                recommendations = response.json()
                st.success(f"Generated {len(recommendations)} recommendations")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.divider()
    st.subheader("About")
    st.info(
        "Data Pipeline Monitor v1.0.0\n\n"
        "Real-time monitoring and optimization system for data pipelines."
    )
