import streamlit as st
import pandas as pd
import pickle
from supabase import create_client
from datetime import datetime
import os
from dotenv import load_dotenv
from pages import login, vehicle_form, predictions, llm_analysis

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Load ML model
# with open('model.pkl', 'rb') as f:
#     model = pickle.load(f)

# Load LLM model (placeholder - replace with your actual LLM model initialization)
llm_model = None  # Your LLM model initialization here

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# Navigation bar
def navigation_bar():
    col1, col2, col3 = st.columns([6,1,1])
    with col1:
        st.title("Vehicle Maintenance Predictor")
    
    if not st.session_state.authenticated:
        with col2:
            if st.button("Login"):
                st.session_state.current_page = 'login'
        with col3:
            if st.button("Sign Up"):
                st.session_state.current_page = 'signup'
    else:
        with col2:
            if st.button("Home"):
                st.session_state.current_page = 'vehicle_form'
        with col3:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.current_page = 'login'

# Main app routing
def main():
    navigation_bar()
    
    if not st.session_state.authenticated:
        if st.session_state.current_page == 'login':
            login.show_login_page(supabase)
        elif st.session_state.current_page == 'signup':
            login.show_signup_page(supabase)
    else:
        if st.session_state.current_page == 'vehicle_form':
            vehicle_form.show_vehicle_form(supabase)
        elif st.session_state.current_page == 'predictions':
            predictions.show_predictions(supabase)
        elif st.session_state.current_page == 'llm_analysis':
            llm_analysis.show_llm_analysis(llm_model)

if __name__ == "__main__":
    main()
