import os
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
import os
# ... (rest of your code remains exactly the same)

# Update Line 26 to handle paths dynamically:
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'mould_predictive_model.pkl')
joblib.dump(model, model_path)

print(f"Predictive maintenance model successfully trained and exported to: {model_path}")

joblib.dump(model, 'src/mould_predictive_model.pkl')
print("Model trained and exported successfully!")