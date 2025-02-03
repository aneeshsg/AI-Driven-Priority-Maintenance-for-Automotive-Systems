import streamlit as st
import pandas as pd
import pickle
import numpy as np
from supabase import Client
from typing import Dict, List, Any
import lightgbm as lgb

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        obj = pickle.load(f)
        if isinstance(obj, lgb.Booster):  
            # Create a new model and assign the Booster object to it
            model = lgb.LGBMModel()
            model._Booster = obj  # Use _Booster directly instead of booster_
            return model
        return obj

# Load the scaler and model
scaler = load_pickle("scaler.pkl")
model = load_pickle("lgbm.pkl")


FEATURES = [
    'Engine_Load', 'Engine_RPM', 'Engine_Coolant_Temp', 'Vibration',
    'Mass_Air_Flow_Rate', 'Engine_Oil_Temp', 'Throttle_Pos_Manifold',
    'Accel_Ssor_Total', 'Trip_Distance', 'Trip_Time_journey', 'Turbo_Boost_And_Vcm_Gauge'
]

feature_select = [
    "Vehicle_speed_sensor", "Vibration", "Engine_Load", "Engine_Coolant_Temp",
    "Engine_RPM", "Speed_OBD", "Mass_Air_Flow_Rate", "Engine_Oil_Temp",
    "Speed_GPS", "Turbo_Boost_And_Vcm_Gauge", "Trip_Distance",
    "Litres_Per_100km_Inst", "CO2_in_g_per_km_Inst", "Trip_Time_journey"
]


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
    st.header("Vehicle Predictions")
    
    try:
        response = supabase.table('vehicles') \
                           .select("*") \
                           .eq('user_id', st.session_state.user.id) \
                           .execute()
        
        if response.data:
            st.write("Debug - Response has data", response.data)
            df = pd.DataFrame(response.data)
            st.write("Debug - DataFrame created", df.head())

            # Ensure correct feature matching
            if set(feature_select) != set(model.feature_name_):
                missing_features = set(model.feature_name_) - set(feature_select)
                extra_features = set(feature_select) - set(model.feature_name_)
                st.error(f"Feature mismatch! Missing: {missing_features}, Extra: {extra_features}")
                return

            predictions: List[Dict[str, Any]] = []
            
            with st.spinner("Running predictions..."):
                for idx, row in df.iterrows():
                    try:
                        all_feature_df = df[feature_select].copy()
                        all_feature_df.loc[:, FEATURES] = scaler.transform(all_feature_df[FEATURES])
                        
                        condition_score = calculate_condition_score(all_feature_df)
                        all_feature_df.loc[:, 'Condition_Score'] = condition_score
                        calc_risk(all_feature_df)

                        feature_names = model.feature_name()
                        all_feature_df = all_feature_df[feature_names] 

                        prediction = model.predict(all_feature_df,FutureWarning=feature_names)
                        prediction_score = np.argmax(prediction, axis=1) if prediction.ndim > 1 else np.argmax(prediction)
                        st.write("Debug - Prediction Score", prediction_score)

                        predictions.append({
                            'vehicle_id': row['vehicle_id'],
                            'user_id': row['user_id'],
                            'prediction_score': prediction_score
                        })
                    except ValueError as ve:
                        st.error(f"Error processing vehicle {row.get('vehicle_id', idx)}: Invalid numeric value. Details: {ve}")
                        continue
                    except Exception as ex:
                        st.error(f"Unexpected error processing vehicle {row.get('vehicle_id', idx)}: {ex}")
                        continue
            
            if predictions:
                predictions_df = pd.DataFrame(predictions).sort_values('prediction_score', ascending=False)
                
                st.subheader("Predictions (Sorted by Score)")
                st.dataframe(predictions_df, hide_index=True)
                
                st.subheader("Select Vehicle for Analysis")
                for _, pred_row in predictions_df.iterrows():
                    btn_label = f"🔍 Analyze Vehicle {pred_row['vehicle_id']} (Score: {pred_row['prediction_score']:.2f})"
                    if st.button(btn_label, key=f"btn_{pred_row['vehicle_id']}"):
                        st.session_state.current_vehicle = pred_row['user_id']
                        st.session_state.current_vehicle_data = pred_row
                        st.session_state.current_page = 'llm_analysis'
                        st.experimental_rerun()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Back to Vehicle Form"):
                    st.session_state.current_page = 'vehicle_form'
                    st.experimental_rerun()
                    
    except Exception as e:
        st.error(f"Error processing predictions: {str(e)}")
