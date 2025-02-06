import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import Client
from typing import Dict, Any
import logging

def show_vehicle_update_form(supabase: Client):
    # Fetch the vehicle_id from session state for updating
    vehicle_id = st.session_state.get('vehicle_id_to_update')

    if vehicle_id:
        st.header(f"Update Vehicle {vehicle_id} Details")
        st.write("Add your recent vehicle details in the form given below to analyse and predict its maintenance requirements.")
        st.write('---------------------')

        # Fetch the vehicle details
        try:
            response = supabase.table("vehicles").select("*").eq("vehicle_id", vehicle_id).execute()

            if response and response.data:
                vehicle_data = response.data[0]

                col1, col2 = st.columns(2)
                
                # Start the form
                with st.form(key="vehicle_update_form"):
                    # Display current vehicle data and allow user to update
                    with col1:
                        brand = st.text_input("Car Brand", value=vehicle_data.get("brand", ""))
                        model_name = st.text_input("Car Model", value=vehicle_data.get("model_name", ""))

                        # Handling the datetime format error
                        last_serviced_date_str = vehicle_data.get("last_serviced_date", "")
                        if last_serviced_date_str:
                            last_serviced_date = datetime.strptime(last_serviced_date_str.split('T')[0], "%Y-%m-%d").date()
                        else:
                            last_serviced_date = datetime.now().date()
                        
                        last_serviced_date = st.date_input("Last Service Date", value=last_serviced_date)

                        vehicle_speed_sensor = st.text_input("Vehicle Speed Sensor", value=str(vehicle_data.get("vehicle_speed_sensor", "")))
                        vibration = st.text_input("Vibration", value=str(vehicle_data.get("vibration", "")))
                        engine_load = st.text_input("Engine Load", value=str(vehicle_data.get("engine_load", "")))
                        engine_coolant_temp = st.text_input("Engine Coolant Temperature", value=str(vehicle_data.get("engine_coolant_temp", "")))
                        co2_in_g_per_km_inst = st.text_input("CO2 in g per km Instant", value=str(vehicle_data.get("co2_in_g_per_km_inst", "")))

                    with col2:
                        mass_air_flow_rate = st.text_input("Mass Air Flow Rate", value=str(vehicle_data.get("mass_air_flow_rate", "")))
                        engine_oil_temp = st.text_input("Engine Oil Temp", value=str(vehicle_data.get("engine_oil_temp", "")))
                        speed_gps = st.text_input("Speed GPS", value=str(vehicle_data.get("speed_gps", "")))
                        turbo_boost_vcm = st.text_input("Turbo Boost and VCM Gauge", value=str(vehicle_data.get("turbo_boost_and_vcm_gauge", "")))
                        trip_distance = st.text_input("Trip Distance", value=str(vehicle_data.get("trip_distance", "")))
                        trip_time_journey = st.text_input("Trip Time Journey", value=str(vehicle_data.get("trip_time_journey", "")))
                        engine_rpm = st.text_input("Engine RPM", value=str(vehicle_data.get("engine_rpm", "")))
                        litres_per_100km_inst = st.text_input("Litres Per 100km Instant", value=str(vehicle_data.get("litres_per_100km_inst", "")))

                    # Optional file uploader, pre-fill with existing manual link if available
                    manual_link_file = st.file_uploader("Upload Manual (PDF)", type=["pdf"])

                    # Submit button
                    submitted = st.form_submit_button("Update Vehicle")

                    if submitted:
                        if not all([vehicle_speed_sensor, vibration, engine_load, engine_coolant_temp, engine_rpm]):
                            st.error("Please fill all required fields")
                        elif manual_link_file is None and vehicle_data.get("manual_link") is None:
                            st.error("Please upload a vehicle manual")
                        else:
                            try:
                                # If a new file is uploaded, update it in Supabase Storage
                                file_url = vehicle_data.get("manual_link")
                                if manual_link_file is not None:
                                    file_name = f"manuals/{st.session_state.user.id}_{manual_link_file.name}"
                                    file_bytes = manual_link_file.read()
                                    response = supabase.storage.from_("manuals").upload(
                                        file_name, file_bytes, file_options={"content-type": manual_link_file.type}
                                    )

                                    if response:
                                        file_url = supabase.storage.from_("manuals").get_public_url(file_name)

                                # Update the vehicle data
                                updated_vehicle_data = {
                                    "brand": brand,
                                    "model_name": model_name,
                                    "last_serviced_date": last_serviced_date.isoformat(),
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
                                    "last_modified": datetime.now().isoformat()
                                }
                                                               
                                # Update the vehicle data in Supabase
                                supabase.table('vehicles').update(updated_vehicle_data).eq("vehicle_id", vehicle_id).execute()

                                st.success("Vehicle updated successfully!")
                            except ValueError as e:
                                st.error(f"Error processing input: {e}")
                            except Exception as e:
                                st.error(f"Error updating vehicle: {str(e)}")

            else:
                st.error(f"No vehicle found with ID {vehicle_id}")

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Go to Form and vehicle list", type="secondary"):
                    st.session_state.current_page = 'vehicle_form'

        except Exception as e:
            st.error(f"Error fetching vehicle details: {str(e)}")
