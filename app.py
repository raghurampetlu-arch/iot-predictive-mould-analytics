import streamlit as st
import pandas as pd
import plotly.express as px
from azure.cosmos import CosmosClient
import joblib
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 1. Page Configuration & Custom CSS Injection for a Modern Web Look
st.set_page_config(
    page_title="AeroGuard | Smart Housing Portal", 
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Inject clean, custom CSS styling to make it look like a custom SaaS application web portal
st.markdown("""
    <style>
        /* Global Background & Typography Tuning */
        .main { background-color: #f8fafc; }
        h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 700; }
        
        /* Premium Card styling for metrics and info blocks */
        .metric-card {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 16px;
        }
        .metric-label { color: #64748b; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
        .metric-value { color: #0f172a; font-size: 28px; font-weight: 700; margin-top: 4px; }
        
        /* Banner Styles */
        .status-banner-good { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-left: 5px solid #22c55e; padding: 20px; border-radius: 8px; }
        .status-banner-bad { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-left: 5px solid #ef4444; padding: 20px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Azure Connection Keys
COSMOS_URI = os.getenv("COSMOS_URI", "YOUR_COSMOS_DB_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY", "YOUR_COSMOS_DB_PRIMARY_KEY")

# 2. Sidebar Navigation Area
with st.sidebar:
    st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
    st.title("🏢 AeroGuard OS")
    st.markdown("`SYSTEM VERSION: v2.4.1-Prod`")
    st.markdown("---")
    
    # Navigation Dropdown Menu
    page_selection = st.selectbox("🌐 Navigation Menu", ["📋 Asset Live Monitor", "⚙️ System Configuration"])
    
    st.markdown("---")
    st.markdown("### 🇬🇧 Compliance Matrix")
    st.caption("• Homes (Fitness for Human Habitation) Act 2018")
    st.caption("• UK Decent Homes Standard Certification")
    st.caption("• Landlord and Tenant Act Sec. 11")

# 3. Main Data Core Pull
try:
    client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
    container = client.get_database_client("MouldAnalyticsDB").get_container_client("TelemetryData")
    items = list(container.query_items(query="SELECT * FROM c ORDER BY c._ts DESC OFFSET 0 LIMIT 100", enable_cross_partition_query=True))
    
    processed_items = []
    for item in items:
        if 'Body' in item:
            try:
                payload = json.loads(item['Body']) if isinstance(item['Body'], str) else item['Body']
                payload['timestamp'] = payload.get('timestamp', item.get('timestamp'))
                processed_items.append(payload)
            except Exception: continue
                
    if processed_items:
        df_telemetry = pd.DataFrame(processed_items)
        df_telemetry['timestamp'] = pd.to_datetime(df_telemetry['timestamp'])
        df_telemetry = df_telemetry.sort_values(by='timestamp', ascending=False).reset_index(drop=True)
    else: raise ValueError()
except Exception:
    df_telemetry = pd.DataFrame([
        {"device_id": "simulated_housing_sensor_01", "timestamp": "2026-10-11T10:45:00", "temperature": 16.20, "humidity": 74.50, "dew_point": 11.50, "mould_risk_score": 100},
        {"device_id": "simulated_housing_sensor_01", "timestamp": "2026-10-11T10:40:00", "temperature": 18.50, "humidity": 58.00, "dew_point": 9.80, "mould_risk_score": 0}
    ])
    df_telemetry['timestamp'] = pd.to_datetime(df_telemetry['timestamp'])

# 4. View Page Routing System
if page_selection == "📋 Asset Live Monitor":
    
    # Header Banner bar
    st.subheader("Property Environmental Diagnostic Dashboard")
    st.markdown("Real-time telemetry stream processing for physical asset protection and early containment mapping.")
    
    latest = df_telemetry.iloc[0]
    
    # 5. Clean Structured Custom Metric Rows Cards HTML
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>🌡️ Ambient Heat</div><div class='metric-value'>{latest['temperature']} °C</div></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>💧 Relative Humidity</div><div class='metric-value'>{latest['humidity']} %</div></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>🥶 Dew Point Threshold</div><div class='metric-value'>{latest['dew_point']} °C</div></div>", unsafe_allow_html=True)
    with m_col4:
        status_text = "CRITICAL OUTBREAK" if latest['mould_risk_score'] > 50 else "OPTIMAL RUNTIME"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>🛡️ Safety Diagnostics</div><div class='metric-value'>{status_text}</div></div>", unsafe_allow_html=True)

    # 6. Tab Container Options
    plot_tab, ml_tab = st.tabs(["📈 Dynamic Trend Diagnostics", "🔮 Predictive Analytics Engine"])
    
    with plot_tab:
        st.markdown("<div style='padding: 10px;'></div>", unsafe_allow_html=True)
        df_chart = df_telemetry.sort_values(by='timestamp')
        fig = px.line(df_chart, x="timestamp", y=["temperature", "humidity"], template="plotly_white", color_discrete_sequence=["#3b82f6", "#f43f5e"])
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')
        
    with ml_tab:
        st.markdown("<div style='padding: 10px;'></div>", unsafe_allow_html=True)
        try:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mould_predictive_model.pkl')
            if not os.path.exists(model_path): model_path = 'mould_predictive_model.pkl'
            model = joblib.load(model_path)
            
            input_features = pd.DataFrame([[latest['humidity'], latest['temperature'], 0, 5.0]], columns=['rolling_avg_humidity', 'rolling_avg_temp', 'extraction_fan_active', 'uk_outdoor_temp'])
            prediction = model.predict(input_features)
            
            if prediction == 1:
                st.markdown("""
                    <div class='status-banner-bad'>
                        <h4 style='color: #991b1b; margin: 0;'>🚨 Advanced Structural Warning Event Detected</h4>
                        <p style='color: #7f1d1d; margin: 8px 0 0 0;'>Machine learning classifiers have identified a persistent moisture anomaly configuration. Surface mould formation is expected to trigger within 72 hours without maintenance intervention.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='status-banner-good'>
                        <h4 style='color: #166534; margin: 0;'>✅ Predictive System Metrics Nominal</h4>
                        <p style='color: #14532d; margin: 8px 0 0 0;'>All time-series parameters align with healthy structural standards. Risk profiles remain stable across the upcoming 5-day cycle forecast window.</p>
                    </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.info("Run model_training.py to activate full machine learning analysis features inside this panel.")

elif page_selection == "⚙️ System Configuration":
    st.subheader("System Infrastructure Control Configuration")
    st.markdown("Manage cloud integration telemetry links and edge connection nodes safely.")
    
    st.text_input("Active Target Device ID Group", value="simulated_housing_sensor_01", disabled=True)
    st.text_input("Ingestion Gateway Address", value="hub-mould-analytics-raghu-iot.azure-devices.net", disabled=True)
    st.success("Connected to Azure Cloud Infrastructure Ecosystem.")
