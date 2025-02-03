import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load the scaler and model (replace with actual paths to your files)
def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# Load the scaler and model
scaler = load_pickle("scaler.pkl")  # Path to your scaler.pkl
model = load_pickle("lgbm.pkl")     # Path to your lgbm.pkl model

# Synthetic input data - replace with appropriate values for your model
synthetic_data = {
    'Engine_Load': 25.5,
    'Engine_RPM': 3000,
    'Engine_Coolant_Temp': 95,
    'Vibration': 0.02,
    'Mass_Air_Flow_Rate': 15.8,
    'Engine_Oil_Temp': 80,
    'Throttle_Pos_Manifold': 40.0,
    'Accel_Ssor_Total': 0.8,
    'Trip_Distance': 150.5,
    'Trip_Time_journey': 2.3,
    'Turbo_Boost_And_Vcm_Gauge': 1.1,
    'Vehicle_Speed_Sensor': 120,
    'Intake_Manifold_Pressure': 75,
    'Speed_OBD': 100,
    'Intake_Air_Temp': 35,
    'Voltage_Control_Module': 12.5,
    'Ambient_Air_Temp': 22,
    'Accel_Pedal_Pos_D': 35.2,
    'Speed_GPS': 115,
    'Litres_Per_100km_Inst': 8.2,
    'CO2_in_g_per_km_Inst': 180
}

# Convert to DataFrame to match the input structure for the model
df = pd.DataFrame([synthetic_data])

# Extract relevant features from the DataFrame
features = [
    df['Engine_Load'][0], df['Engine_RPM'][0], df['Engine_Coolant_Temp'][0], df['Vibration'][0],
    df['Mass_Air_Flow_Rate'][0], df['Engine_Oil_Temp'][0], df['Throttle_Pos_Manifold'][0],
    df['Accel_Ssor_Total'][0], df['Trip_Distance'][0], df['Trip_Time_journey'][0],
    df['Turbo_Boost_And_Vcm_Gauge'][0], df['Vehicle_Speed_Sensor'][0],
    df['Intake_Manifold_Pressure'][0], df['Speed_OBD'][0], df['Intake_Air_Temp'][0],
    df['Voltage_Control_Module'][0], df['Ambient_Air_Temp'][0], df['Accel_Pedal_Pos_D'][0],
    df['Speed_GPS'][0], df['Litres_Per_100km_Inst'][0], df['CO2_in_g_per_km_Inst'][0]
]

# Convert to NumPy array and reshape
features = np.array(features).reshape(1, -1)

# Apply scaling
features_scaled = scaler.transform(features)

# Make prediction
prediction_score = model.predict(features_scaled)[0]

# Output the prediction score
print(f"Prediction Score: {prediction_score}")
