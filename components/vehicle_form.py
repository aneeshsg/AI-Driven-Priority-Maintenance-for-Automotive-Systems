import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import Client
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_vehicle(supabase: Client, vehicle_id: str):
    try:
        response = supabase.table("vehicles").delete().eq("vehicle_id", vehicle_id).execute()
        if response and response.data:
            st.success(f"Vehicle {vehicle_id} deleted successfully!")
        else:
            st.error("Failed to delete vehicle. Please try again.")
    except Exception as e:
        st.error(f"Error deleting vehicle: {str(e)}")

def show_vehicle_form(supabase: Client):
    st.header("Add Vehicle Details")
    st.write("Add your vehicle details in the form below to analyze and predict its maintenance requirements.")
    st.write('---------------------')
    
    with st.form("vehicle_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.text_input("Car Brand")
            model_name = st.text_input("Car Model")
            last_serviced_date = st.date_input("Last Service Date", min_value=datetime(2000, 1, 1), max_value=datetime.now().date())
            vehicle_id = st.text_input("Enter vehicle id ")
            vehicle_speed_sensor = st.text_input("Vehicle Speed Sensor")
            vibration = st.text_input("Vibration")
            engine_load = st.text_input("Engine Load")
            engine_coolant_temp = st.text_input("Engine Coolant Temperature")
            co2_in_g_per_km_inst = st.text_input("CO2 in g per km Instant")
            
        with col2:
            mass_air_flow_rate = st.text_input("Mass Air Flow Rate")
            engine_oil_temp = st.text_input("Engine Oil Temp")
            speed_gps = st.text_input("Speed GPS")
            turbo_boost_vcm = st.text_input("Turbo Boost and VCM Gauge")
            trip_distance = st.text_input("Trip Distance")
            trip_time_journey = st.text_input("Trip Time Journey")
            engine_rpm = st.text_input("Engine RPM")
            litres_per_100km_inst = st.text_input("Litres Per 100km Instant")
            
            manual_link_file = st.file_uploader("Upload Manual (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Add Vehicle")
    
    if submitted:
        if not all([vehicle_speed_sensor, vibration, engine_load, engine_coolant_temp, engine_rpm]):
            st.error("Please fill all required fields")
        elif manual_link_file is None:
            st.error("Please upload a vehicle manual")
        else:
            try:
                file_name = f"manuals/{st.session_state.user.id}_{manual_link_file.name}"
                file_bytes = manual_link_file.read()
                response = supabase.storage.from_("manuals").upload(file_name, file_bytes, file_options={"content-type": manual_link_file.type})
                
                if response:
                    file_url = supabase.storage.from_("manuals").get_public_url(file_name)
                    vehicles: Dict[str, Any] = {
                        "user_id": st.session_state.user.id,
                        "vehicle_id": vehicle_id,
                        "brand": brand,
                        "model_name": model_name,
                        "last_serviced_date": last_serviced_date.isoformat(),
                        "added_on": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "vehicle_speed_sensor": float(vehicle_speed_sensor),
                        "vibration": float(vibration),
                        "engine_load": float(engine_load),
                        "engine_coolant_temp": float(engine_coolant_temp),
                        "engine_rpm": float(engine_rpm),
                        "mass_air_flow_rate": float(mass_air_flow_rate) if mass_air_flow_rate else None,
                        "engine_oil_temp": float(engine_oil_temp) if engine_oil_temp else None,
                        "speed_gps": float(speed_gps) if speed_gps else None,
                        "turbo_boost_and_vcm_gauge": float(turbo_boost_vcm) if turbo_boost_vcm else None,
                        "trip_distance": float(trip_distance) if trip_distance else None,
                        "litres_per_100km_inst": float(litres_per_100km_inst) if litres_per_100km_inst else None,
                        "co2_in_g_per_km_inst": float(co2_in_g_per_km_inst) if co2_in_g_per_km_inst else None,
                        "trip_time_journey": float(trip_time_journey) if trip_time_journey else None,
                        "manual_link": file_url,
                        "score": None
                    }
                    
                    supabase.table('vehicles').insert(vehicles).execute()
                    st.success("Vehicle added successfully!")
                else:
                    st.error("Failed to upload manual file.")
            except Exception as e:
                st.error(f"Error adding vehicle: {str(e)}")

    try:
        response = supabase.table("vehicles").select("*").eq("user_id", st.session_state.user.id).execute()
        if response and response.data:
            df = pd.DataFrame(response.data)
            st.subheader("Current Vehicles")
            st.write('List of all added vehicles, click to update or delete.')
            st.write('------------------------------------------------------------------------')
            st.dataframe(df)
            
            for index, row in df.iterrows():
                with st.expander(f"Vehicle {row['vehicle_id']} Details"):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"Update {row['vehicle_id']}", key=f"update_{row['vehicle_id']}"):
                            st.session_state.current_page = 'update'
                            st.session_state.vehicle_id_to_update = row['vehicle_id']
                    with col2:
                        if st.button(f"Delete {row['vehicle_id']}", key=f"delete_{row['vehicle_id']}"):
                            delete_vehicle(supabase, row['vehicle_id'])
                            st.experimental_rerun()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Go to Predictions", type="secondary"):
                    st.session_state.current_page = 'predictions'
    except Exception as e:
        st.error(f"Error fetching vehicles: {str(e)}")
