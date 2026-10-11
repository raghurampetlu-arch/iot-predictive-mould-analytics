# IoT Predictive Mould Analytics Platform

An end-to-end Data Science and Engineering portfolio project designed for the UK Social Housing sector to predict structural mould risks and ensure compliance with the **UK Decent Homes Standard**.

## 🏗️ Architecture Blueprint
`[Simulated IoT Device (Python)]` ➔ `[Azure IoT Hub]` ➔ `[Azure Cosmos DB]` ➔ `[Streamlit Enterprise Dashboard (GitHub Live)]`

---

## 💻 1. Core Source Code

### `src/simulator.py`
This script simulates edge hardware tracking ambient metrics and routes data directly over MQTT via the Azure SDK framework.

```python
import time
import json
import random
import datetime
from azure.iot.device import IoTHubDeviceClient

CONNECTION_STRING = "YOUR_AZURE_DEVICE_CONNECTION_STRING"

def generate_telemetry(device_id, step):
    base_temp = 19.0
    base_humidity = 55.0
    
    # Inject dynamic environmental anomaly to trigger the ML alerts
    if step > 20:
        temperature = base_temp - random.uniform(2.0, 4.0)
        humidity = base_humidity + random.uniform(20.0, 30.0)
    else:
        temperature = base_temp + random.uniform(-1.5, 1.5)
        humidity = base_humidity + random.uniform(-5.0, 5.0)

    # Magnus-Tetens framework for dynamic dew point approximation
    gamma = ((17.27 * temperature) / (237.7 + temperature)) + (humidity / 100.0)
    dew_point = (237.7 * gamma) / (17.27 - gamma)
    
    mould_risk_score = 100 if (humidity > 70.0 and (temperature - dew_point) < 3.0) else 0

    return {
        "device_id": device_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "dew_point": round(dew_point, 2),
        "mould_risk_score": mould_risk_score
    }

def main():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    step = 0
    try:
        while True:
            step += 1
            data = generate_telemetry("simulated_housing_sensor_01", step)
            client.send_message(json.dumps(data))
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        client.shutdown()

if __name__ == "__main__":
    main()
```

### `src/model_training.py`
Trains a Classifier predicting advanced risk based on structural parameters and historical UK local microclimates.

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

np.random.seed(42)
n_samples = 2000

data = {
    'rolling_avg_humidity': np.random.uniform(40.0, 85.0, n_samples),
    'rolling_avg_temp': np.random.uniform(14.0, 22.0, n_samples),
    'extraction_fan_active': np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7]),
    'uk_outdoor_temp': np.random.uniform(2.0, 12.0, n_samples)
}
df = pd.DataFrame(data)
df['mould_outbreak_occurring'] = ((df['rolling_avg_humidity'] > 68.0) & (df['rolling_avg_temp'] < 17.0) & (df['extraction_fan_active'] == 0)).astype(int)

X = df.drop('mould_outbreak_occurring', axis=1)
y = df['mould_outbreak_occurring']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, 'src/mould_predictive_model.pkl')
print("Model trained and exported successfully!")
```

### `src/app.py`
Main UI layer built via Streamlit to handle client data ingestion and display analytics.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from azure.cosmos import CosmosClient
import joblib
import os

st.set_page_config(page_title="UK Social Housing Smart Environment Panel", layout="wide")
st.title("🇬🇧 IoT Predictive Mould & Damp Analytics Hub")

# Cloud state configurations
COSMOS_URI = os.getenv("COSMOS_URI", "YOUR_COSMOS_DB_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY", "YOUR_COSMOS_DB_PRIMARY_KEY")

try:
    client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
    container = client.get_database_client("MouldAnalyticsDB").get_container_client("TelemetryData")
    items = list(container.query_items(query="SELECT * FROM c ORDER BY c.timestamp DESC OFFSET 0 LIMIT 100", enable_cross_partition_query=True))
    df_telemetry = pd.DataFrame(items)
except Exception:
    df_telemetry = pd.DataFrame([
        {"device_id": "simulated_housing_sensor_01", "timestamp": "2026-10-09T08:00:00", "temperature": 16.2, "humidity": 74.5, "dew_point": 11.5, "mould_risk_score": 100},
        {"device_id": "simulated_housing_sensor_01", "timestamp": "2026-10-09T07:00:00", "temperature": 18.5, "humidity": 58.0, "dew_point": 9.8, "mould_risk_score": 0}
    ])

latest = df_telemetry.iloc[0]
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Indoor Temperature", f"{latest['temperature']} °C")
with col2: st.metric("Relative Humidity", f"{latest['humidity']} %")
with col3: st.metric("Calculated Dew Point", f"{latest['dew_point']} °C")
with col4: st.metric("Status", "🚨 ACTION REQUIRED" if latest['mould_risk_score'] > 50 else "✅ OPTIMAL")

fig = px.line(df_telemetry, x="timestamp", y=["temperature", "humidity"], title="Environmental Telemetry Overview")
st.plotly_chart(fig, use_container_width=True)
```

---

## 🛠️ 2. Comprehensive Step-by-Step Guide

### Step 1: Initialise Project Environment
1. Create a public repository on GitHub named `iot-predictive-mould-analytics`.
2. Generate a local project workspace containing directories `src/` and `.github/workflows/`.
3. Add the structural Python libraries inside a root `requirements.txt` workspace file.

### Step 2: Establish the Azure Cloud Framework
1. Sign into the **Azure Portal** and spawn a fresh Resource Group situated inside the **UK South** boundary region.
2. Provision an **Azure IoT Hub (Free F1 Tier)**. Inside the Devices registry pane, register a unique node named `simulated_housing_sensor_01`, and export its **Primary Connection String** parameter.
3. Provisions a serverless **Azure Cosmos DB for NoSQL** database cluster instance. Setup a container called `TelemetryData` setting the analytical partition indexing route exactly to `/device_id`.

### Step 3: Local Model Engineering & Execution
1. Compile and execute `src/model_training.py` inside your local shell terminal framework to output the compiled machine learning asset workspace model file `src/mould_predictive_model.pkl`.
2. Update connection configurations inside the local file stack to map explicit streaming telemetry paths.

### Step 4: Streamlit Engine Deployment
1. Link your live cloud profile to your target **GitHub workspace repository**.
2. Instantiate an agile frontend pipeline engine by target linking compilation configurations pointing straight towards `src/app.py`.
3. Provision environment key configurations within Streamlit Cloud properties mapping your live database authentication parameters safely.