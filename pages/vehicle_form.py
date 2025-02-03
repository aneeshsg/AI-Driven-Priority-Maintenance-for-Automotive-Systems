import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import Client
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_vehicle_form(supabase: Client):
    st.header("Add Vehicle Details")
    
    with st.form("vehicle_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            vehicle_id = st.text_input("Enter vehicle id ")
            engine_load = st.text_input("Engine Load")
            engine_rpm = st.text_input("Engine RPM")
            engine_coolant_temp = st.text_input("Engine Coolant Temperature")
            mass_air_flow_rate = st.text_input("Mass Air Flow Rate")
            engine_oil_temp = st.text_input("Engine Oil Temp")
            throttle_pos_manifold = st.text_input("Throttle Position Manifold")
            accel_ssor_total = st.text_input("Accelerator Sensor Total")

        with col2:
            trip_distance = st.text_input("Trip Distance")
            trip_time_journey = st.text_input("Trip Time Journey")
            vibration = st.text_input("Vibration")
            turbo_boost_vcm = st.text_input("Turbo Boost and VCM Gauge")
            vehicle_speed_sensor = st.text_input("Vehicle Speed Sensor")
            intake_manifold_pressure = st.text_input("Intake Manifold Pressure")
            speed_obd = st.text_input("Speed OBD")
            intake_air_temp = st.text_input("Intake Air Temp")
            voltage_control_module = st.text_input("Voltage Control Module")
            ambient_air_temp = st.text_input("Ambient Air Temp")
            accel_pedal_pos_d = st.text_input("Accelerator Pedal Position D")
            speed_gps = st.text_input("Speed GPS")
            litres_per_100km_inst = st.text_input("Litres Per 100km Instant")
            co2_in_g_per_km_inst = st.text_input("CO2 in g per km Instant")
            
            # Add file uploader
            manual_link_file = st.file_uploader("Upload Manual (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Add Vehicle")

    if submitted:
        # Check that all required fields are filled
        if not all([vehicle_id,engine_load, engine_rpm, engine_coolant_temp, trip_distance, trip_time_journey, vibration]):
            st.error("Please fill all required fields and upload the manual file")
        else:
            try:
                # Upload the file to Supabase Storage
                if manual_link_file is not None:
                    # Construct the file path in Supabase Storage
                    file_name = f"manuals/{st.session_state.user.id}_{manual_link_file.name}"
                    file_bytes = manual_link_file.read()

                    # Upload file to Supabase Storage (manual_link_file is already file-like)
                    response = supabase.storage.from_("manuals").upload(
                        file_name, file_bytes, file_options={"content-type": manual_link_file.type}
                    )

                    if response:
                        # Get the public URL of the uploaded file
                        file_url = supabase.storage.from_("manuals").get_public_url(file_name)
                        st.success(f"File uploaded successfully: {file_url}")
                    else:
                        st.error("Failed to upload file.")

                # Prepare the vehicle data dictionary
                vehicles: Dict[str, Any] = {
                    
                    "user_id": st.session_state.user.id,#
                    "vehicle_id": str(vehicle_id),  # You can modify this logic for generating a unique vehicle_id #
                    # You can calculate or input the score later
                    "added_on": datetime.now().isoformat(),  # Converts datetime to string
                    "last_modified": datetime.now().isoformat(),
                    "engine_load": float(engine_load),#
                    "engine_rpm": float(engine_rpm),#
                    "engine_coolant_temp": float(engine_coolant_temp),#
                    "vibration": float(vibration),#
                    "mass_air_flow_rate": float(mass_air_flow_rate) if mass_air_flow_rate else None,#
                    "engine_oil_temp": float(engine_oil_temp) if engine_oil_temp else None,#
                    "throttle_pos_manifold": float(throttle_pos_manifold) if throttle_pos_manifold else None,#
                    "trip_distance": float(trip_distance),#
                    "trip_time_journey": float(trip_time_journey),#
                    "turbo_boost_vcm": float(turbo_boost_vcm) if turbo_boost_vcm else None,#
                    "vehicle_speed_sensor": float(vehicle_speed_sensor) if vehicle_speed_sensor else None,#
                    "intake_manifold_pressure": float(intake_manifold_pressure) if intake_manifold_pressure else None,#
                    "speed_obd": float(speed_obd) if speed_obd else None,#
                    "intake_air_temp": float(intake_air_temp) if intake_air_temp else None,#
                    "voltage_control_module": float(voltage_control_module) if voltage_control_module else None,#
                    "ambient_air_temp": float(ambient_air_temp) if ambient_air_temp else None,#
                    "accel_pedal_pos_d": float(accel_pedal_pos_d) if accel_pedal_pos_d else None,#
                    "speed_gps": float(speed_gps) if speed_gps else None,#
                    "litres_per_100km_inst": float(litres_per_100km_inst) if litres_per_100km_inst else None,#
                    "co2_in_g_per_km_inst": float(co2_in_g_per_km_inst) if co2_in_g_per_km_inst else None,#
                    "accel_ssor_total":float(accel_ssor_total) if accel_ssor_total else None,#
                    "manual_link": file_url,  # Store the file URL in the manual_link field,
                    "score":None
                }
                st.write("Debug - User ID:", vehicles)
                # Insert the vehicle data into the Supabase table
                supabase.table('vehicles').insert(vehicles).execute()

                st.success("Vehicle added successfully!")

            except ValueError as e:
                st.error(f"Error processing input: {e}")
            except Exception as e:
                st.error(f"Error adding vehicle: {str(e)}")

    # Display vehicles table
    try:
        # st.write("Debug - User ID:", st.session_state.user.id)
        
        # Debug point 2: Print before database query
        # st.write("Debug - Attempting database query...")
        
        response = supabase.table('vehicles').select("*").eq('user_id', st.session_state.user.id).execute()
        # logger.info(f"Response received: {response}")
        
        if response and response.data:
            # st.write("Debug - Response has data")
            # st.write("Debug - Number of records:", len(response.data))
            
            df = pd.DataFrame(response.data)
            # st.write("Debug - DataFrame shape:", df.shape)
            
            st.subheader("Current Vehicles")
            st.dataframe(df)
            
            col1, col2 , col3  = st.columns([1, 1, 1])
            with col2:
                if st.button("Go to Predictions", type="primary"):
                    st.session_state.current_page = 'predictions'
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Error fetching vehicles: {str(e)}")
        # Debug point 4: Print full error traceback
        import traceback
        st.write("Debug - Full error:", traceback.format_exc())
