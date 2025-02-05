import streamlit as st
import pandas as pd
import pickle
import numpy as np
from supabase import Client
from typing import Dict, List, Any
import lightgbm as lgb

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


feature_select = [
    'Engine_Load', 'Engine_RPM', 'Engine_Coolant_Temp', 'Vibration',
    'Mass_Air_Flow_Rate', 'Engine_Oil_Temp', 'Trip_Distance', 'Trip_Time_journey', 'Turbo_Boost_And_Vcm_Gauge'
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


def show_predictions(supabase: Client):
      
    try:
        response = supabase.table('vehicles') \
                           .select("*") \
                           .eq('user_id', st.session_state.user.id) \
                           .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            df.rename(columns=rename_mapping, inplace=True)
            st.write(df)
            vehicle_id = df['vehicle_id']
            predictions: List[Dict[str, Any]] = []
            
            with st.spinner("Running predictions..."):
                for idx, row in df.iterrows():
                    try:
                        row_df = pd.DataFrame([row])

                        for feature, scaler_obj in scaler.items():
                            if feature in row_df.columns:
                                # scaler_obj.transform expects a 2D array (DataFrame)
                                row_df[feature] = scaler_obj.transform(row_df[[feature]])

                        condition_score = calculate_condition_score(row_df)
                        row_df['Condition_Score'] = condition_score
                        calc_risk(row_df)

                        row_df = row_df[model.feature_name_]
                        
                        pred = model.predict(row_df)[0]
                        pred_prob = model.predict_proba(row_df)[0]
                        prediction_score = np.max(pred_prob)
                        
                        
                        predictions.append({
                            'vehicle_id': row.get('vehicle_id', idx),
                            'prediction': int(pred),
                            'Engine Failure': pred_prob[0],
                            'Overstrain Failure': pred_prob[1],
                            'Heat Dissipation Failure': pred_prob[2],
                            'prediction_score': prediction_score
                        })
                    except Exception as inner_e:
                        st.error(f"Error processing record {idx}: {inner_e}")
            
            if predictions:
                predictions_df = pd.DataFrame(predictions).sort_values('prediction_score', ascending=False)
                
                st.subheader("Predictions (Sorted by Score)")
                st.dataframe(predictions_df, hide_index=True)
                
                st.subheader("Select Vehicle for Analysis")
                for _, pred_row in predictions_df.iterrows():
                    btn_label = f"🔍 Analyze Vehicle {pred_row['vehicle_id']} (Score: {pred_row['prediction_score']:.2f})"
                    if st.button(btn_label, key=f"btn_{pred_row['vehicle_id']}"):
                        st.session_state.current_vehicle = {pred_row['vehicle_id']}
                        st.session_state.current_vehicle_data = pred_row
                        st.session_state.current_page = 'llm_analysis'
                        st.rerun()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Back to Vehicle Form"):
                    st.session_state.current_page = 'vehicle_form'
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Error processing predictions: {str(e)}")

