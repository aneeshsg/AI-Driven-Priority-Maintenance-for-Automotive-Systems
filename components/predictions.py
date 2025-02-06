import streamlit as st
import pandas as pd
import pickle
import numpy as np
from supabase import Client
from typing import Dict, List, Any
import lightgbm as lgb
import datetime

vehicle_id = "some"

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        obj = pickle.load(f)
        if isinstance(obj, dict) and 'model' in obj:
            obj = obj['model']
        if isinstance(obj, lgb.Booster):  
            model = lgb.LGBMModel()
            model._Booster = obj  
            return model
        return obj

scaler = load_pickle("scaler.pkl")
model = load_pickle("lgbm.pkl")

FEATURES = [
    'Engine_Load', 'Engine_RPM', 'Engine_Coolant_Temp', 'Vibration',
    'Mass_Air_Flow_Rate', 'Engine_Oil_Temp', 'Throttle_Pos_Manifold',
    'Accel_Ssor_Total', 'Trip_Distance', 'Trip_Time_journey', 'Turbo_Boost_And_Vcm_Gauge'
]

rename_mapping = {
    'engine_load': 'Engine_Load',
    'engine_rpm': 'Engine_RPM',
    'engine_coolant_temp': 'Engine_Coolant_Temp',
    'vibration': 'Vibration',
    'mass_air_flow_rate': 'Mass_Air_Flow_Rate',
    'engine_oil_temp': 'Engine_Oil_Temp',
    'throttle_pos_manifold': 'Throttle_Pos_Manifold',
    'accel_ssor_total': 'Accel_Ssor_Total',
    'trip_distance': 'Trip_Distance',
    'trip_time_journey': 'Trip_Time_journey',
    'turbo_boost_and_vcm_gauge': 'Turbo_Boost_And_Vcm_Gauge',
    'litres_per_100km_inst': 'Litres_Per_100km_Inst',
    'overstrain_risk': 'Overstrain_Risk',
    'heat_dissipation_risk': 'Heat_Dissipation_Risk',
    'power_failure_risk': 'Power_Failure_Risk',
    'vehicle_speed_sensor': 'Vehicle_speed_sensor',
    'co2_in_g_per_km_inst': 'CO2_in_g_per_km_Inst',
    'condition_score': 'Condition_Score',
    'speed_gps': 'Speed_GPS'
}

def calculate_condition_score(row):
    engine_health_score = (row['Engine_Load'] + row['Engine_RPM'] + row['Engine_Coolant_Temp']) / 3
    usage_severity = row['Engine_Load'] * (row['Trip_Distance'] + row['Trip_Time_journey'])
    anomaly_flag = ((row['Vibration'] > 0.7) | (row['Engine_Coolant_Temp'] > 0.8)).astype(int)
    condition_score = 0.5 * engine_health_score + 0.3 * usage_severity + 0.2 * anomaly_flag
    return condition_score

def calc_risk(df):
    df.loc[:, 'Overstrain_Risk'] = 0.5 * df['Engine_Load'] + 0.5 * df['Engine_RPM']
    df.loc[:, 'Heat_Dissipation_Risk'] = 0.4 * df['Engine_Coolant_Temp'] + 0.6 * df['Engine_Oil_Temp']
    df.loc[:, 'Power_Failure_Risk'] = 0.5 * df['Mass_Air_Flow_Rate'] + 0.5 * df['Turbo_Boost_And_Vcm_Gauge']

columns_to_select = [
            "vehicle_id", "brand", "model_name", "last_serviced_date"
        ]

def show_predictions(supabase: Client):
    st.header("Vehicle Maintainance Predictions")
    st.write("Machine Learning model predictions for all your vehicles and prioritsing the need for maintainance.")
    st.write('---------------------')

    try:
        response = supabase.table('vehicles') \
                           .select("*") \
                           .eq('user_id', st.session_state.user.id) \
                           .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns=rename_mapping, inplace=True)
            table_html = """
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    font-family: Arial, sans-serif;
                }
                th, td {
                    padding: 10px;
                    text-align: center;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                tr:hover {
                    background-color: #f1f1f1;
                }
                .vehicle-card {
                    height: 500px;
                    border: 2px solid #ddd;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    margin-bottom: 15px;
                    transition: all 0.3s ease;
                }
                .vehicle-card:hover {
                    box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.2);
                    transform: scale(1.02);
                }
                .vehicle-card h4 {
                    font-size: 1.2em;
                    margin-bottom: 10px;
                }
                .failure-info {
                    margin-top: 10px;
                    padding: 5px;
                    font-weight: bold;
                }
                .failure-info.red {
                    color: red;
                }
                .failure-info.orange {
                    color: orange;
                }
            </style>
            <table>
                <thead>
                    <tr>
            """
            response = supabase.table("vehicles").select(",".join(columns_to_select)).eq("user_id", st.session_state.user.id).execute()
            df1 = pd.DataFrame(response.data)
            st.write("List of all the vehicles")
            # Add column names dynamically
            for column in df1.columns:
                table_html += f"<th>{column}</th>"
            
            table_html += "</tr></thead><tbody>"

            # Add rows of data
            for idx, row in df1.iterrows():
                table_html += "<tr>"
                for value in row:
                    table_html += f"<td>{value}</td>"
                table_html += "</tr>"

            table_html += "</tbody></table>"

            # Show the raw data table
            st.markdown(table_html, unsafe_allow_html=True)

            predictions: List[Dict[str, Any]] = []

            with st.spinner("Running predictions..."):
                for idx, row in df.iterrows():
                    try:
                        row_df = pd.DataFrame([row])

                        for feature, scaler_obj in scaler.items():
                            if feature in row_df.columns:
                                row_df[feature] = scaler_obj.transform(row_df[[feature]])

                        condition_score = calculate_condition_score(row_df)
                        row_df['Condition_Score'] = condition_score
                        calc_risk(row_df)

                        row_df = row_df[model.feature_name_]

                        pred = model.predict(row_df)[0]
                        pred_prob = model.predict_proba(row_df)

                        # Ensure pred_prob is a NumPy array
                        if isinstance(pred_prob, list):
                            pred_prob = np.array(pred_prob)

                        pred_prob = pred_prob[0]
                        prediction_score = np.max(pred_prob)

                        last_service_date = row.get('last_serviced_date', idx)

                        if last_service_date:
                            try:
                                # Handle ISO 8601 format like "2024-02-23T00:00:00"
                                last_service_date = last_service_date.split("T")[0]  # Keep only "YYYY-MM-DD"
                                last_service_date = datetime.datetime.strptime(last_service_date, "%Y-%m-%d").date()
                            except ValueError:
                                last_service_date = None  # If parsing fails, set to None

                        predictions.append({
                            'vehicle_id': row.get('vehicle_id', idx),
                            'prediction': int(pred),
                            'engine_failure': pred_prob[0],
                            'overstrain_failure': pred_prob[1],
                            'heat_dissipation_failure': pred_prob[2],
                            'prediction_score': prediction_score,
                            'last_serviced_date': last_service_date,
                        })
                    except Exception as inner_e:
                        st.error(f"Error processing record {idx}: {inner_e}")

            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            
            st.write("Predictions for all the vehicles")
            if predictions:
                predictions_df = pd.DataFrame(predictions).sort_values('prediction_score', ascending=False)

                num_cols = 3  # Number of cards per row
                cols = st.columns(num_cols)

                for idx, pred_row in enumerate(predictions_df.itertuples()):
                    col = cols[idx % num_cols]  # Distribute cards across columns

                    # Determine the highest failure type
                    failure_types = {
                        "Engine Failure": pred_row.engine_failure,
                        "Overstrain Failure": pred_row.overstrain_failure,
                        "Heat Dissipation Failure": pred_row.heat_dissipation_failure,
                    }
                    
                    highest_failure = max(failure_types, key=failure_types.get)
                    highest_failure_value = failure_types[highest_failure]

                    # Highlight the highest failure in red
                    def format_failure(name, value):
                        if name == highest_failure:
                            return f'<p class="failure-info red"><b>{name}:</b> {value:.5f}</p>'
                        return f'<p class="failure-info"><b>{name}:</b> {value:.5f}</p>'

                    # Check if maintenance is needed
                    maintenance_warning = ""
                    if pred_row.last_serviced_date:
                        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
                        if pred_row.last_serviced_date < one_year_ago:
                            maintenance_warning = '<p class="failure-info orange"><b>⚠️ General Maintenance Required</b></p>'

                    with col:
                        st.markdown(
                            f"""
                            <div class="vehicle-card">
                                <h4> Vehicle ID: {pred_row.vehicle_id}</h4>
                                {format_failure("Engine Failure", pred_row.engine_failure)}
                                {format_failure("Overstrain Failure", pred_row.overstrain_failure)}
                                {format_failure("Heat Dissipation Failure", pred_row.heat_dissipation_failure)}
                                <p><b>Prev Service Date:</b> {pred_row.last_serviced_date}</p>
                                {maintenance_warning}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if st.button(f"🔍 Analyze {pred_row.vehicle_id}", key=f"btn_{pred_row.vehicle_id}_{idx}") :
                            st.session_state.current_vehicle = {pred_row.vehicle_id}
                            st.session_state.current_vehicle_data = pred_row._asdict()
                            st.session_state.current_page = 'llm_analysis'
                            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
