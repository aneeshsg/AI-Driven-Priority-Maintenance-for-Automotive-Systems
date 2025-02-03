import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Dict
import json

def show_llm_analysis(llm_model: Any):
    st.header(f"Maintenance Analysis for Vehicle {st.session_state.current_vehicle}")
    
    vehicle_data: Dict[str, Any] = st.session_state.current_vehicle_data
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Vehicle Details", "Maintenance Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Vehicle Metrics")
            metrics_data = {k: v for k, v in vehicle_data.items() 
                          if k not in ['id', 'manual_link', 'user_id']}
            
            for key, value in metrics_data.items():
                st.metric(
                    label=key.replace('_', ' ').title(),
                    value=value
                )
        
        with col2:
            st.subheader("Prediction Score")
            score = float(vehicle_data['prediction_score'])
            
            # Create a color based on the score (red for high scores, green for low)
            color = f"{'red' if score > 0.7 else 'orange' if score > 0.4 else 'green'}"
            st.markdown(
                f"""
                <div style='padding: 1rem; background-color: {color}25; border-radius: 0.5rem;'>
                    <h1 style='color: {color}; text-align: center;'>{score:.2f}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with tab2:
        try:
            st.subheader("Maintenance Recommendations")
            
            # Here you would integrate your LLM model
            # Example structure for LLM integration:
            # analysis = llm_model.analyze(
            #     manual_url=vehicle_data['manual_link'],
            #     prediction_score=vehicle_data['prediction_score'],
            #     vehicle_metrics=vehicle_data
            # )
            # st.write(analysis)
            
            st.info("LLM Analysis will be integrated here")
            
        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Back to Predictions"):
            st.session_state.current_page = 'predictions'
            st.rerun()
