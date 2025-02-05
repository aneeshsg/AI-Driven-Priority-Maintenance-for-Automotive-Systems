import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
from pages import login, vehicle_form, predictions, llm_analysis,update
import pandas as pd

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

st.set_page_config(
    page_title="Vehicle Predictive Analysis",
    layout="centered",
)

st.markdown("""
<style>
    .stButton>button {
        color: black;
        background-color: #ffffff;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 8px;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .title {
        font-size: 36px;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 20px;
    }
    .description {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 30px;
    }
    .section-title {
        text-align: center;
        padding-top: 60px;
        font-size: 28px;
        color: #2c3e50;
    }
    
    /* Adjust table style for a consistent look */
    .css-1d391kg table {
        width: 100%;
        border-collapse: collapse;
    }
    .css-1d391kg th, .css-1d391kg td {
        padding: 12px;
        border: 1px solid #ddd;
        text-align: left;
    }
    .css-1d391kg th {
        background-color: #4CAF50;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)


def show_home_page():
    """Renders the home page with a welcome message, features, project description, and team table."""
    
    
    st.markdown("<p class='description'>Advanced analytics and insights for vehicle data management</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Comprehensive Analysis")
        st.write("In-depth predictive modeling and data visualization for vehicle-related metrics.")
    
    with col2:
        st.markdown("#### 🤖 AI-Powered Insights")
        st.write("Leverage advanced machine learning to extract meaningful patterns from your data.")
    
    with col3:
        st.markdown("#### 🔒 Secure Platform")
        st.write("Robust authentication and data protection to ensure your information's safety.")
    
    st.info("Please log in to access all features of the platform.")
    
    # Why This Project Section
    st.markdown("<h2 class='section-title'>Why This Project?</h2>", unsafe_allow_html=True)
    st.write(
        "The Vehicle Predictive Analysis Platform was developed to revolutionize the automotive industry by leveraging "
        "data-driven insights. This project aims to predict vehicle failures before they occur, enabling proactive maintenance, "
        "reducing downtime, and ensuring safety. With advanced analytics and machine learning algorithms, we empower stakeholders "
        "to optimize vehicle performance and reliability."
    )
    
    # Team Members Section
    st.markdown("<h2 class='section-title'>Our Team</h2>", unsafe_allow_html=True)
    team_data = {
        'Name': ['Aneesh SG', 'Aditya Ravi','Sujay K', 'Ganesh Naik','Manojith Bhat'],
        'USN': ['ISE', 'CSE', 'AIML', 'CSE', 'ISE'],
        'Contact': ['aneeshsg.is22@rvce.edu.in', 'adityaravi.cs22@rvce.edu.in', 'sujayak.ai22@rvce.edu.in', 'ganeshnaik.cs22@rvce.edu.in','manojithbhatv.is22@rvce.edu.in']
    }
    df_team = pd.DataFrame(team_data)
    st.table(df_team)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_top_navigation():
    """Renders top navigation based on authentication status."""
    col2, col3, col4,col5,col6 = st.columns([1, 1, 1 ,1,1])
    
    if not st.session_state.authenticated:
        with col2:
            if st.button("Home"):
                st.session_state.current_page = "Home"
                st.experimental_rerun()
        with col5:
            if st.button("Login"):
                st.session_state.current_page = "Login"
                st.experimental_rerun()
        with col6:
            if st.button("Signup"):
                st.session_state.current_page = "Signup"
                st.experimental_rerun()
    else:
        with col2:
            if st.button("Vehicle Form"):
                st.session_state.current_page = "vehicle_form"
                st.experimental_rerun()
        with col3:
            if st.button("Predictions"):
                st.session_state.current_page = "predictions"
                st.experimental_rerun()
        with col4:
            if st.button("Analysis"):
                st.session_state.current_page = "llm_analysis"
                st.experimental_rerun()
        with col6:
            if st.button("Update"):
                st.session_state.current_page = "update"
                st.experimental_rerun()
        with col5:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.current_page = "Home"
                st.success("✅ Logged out successfully!")
                st.experimental_rerun()


def main():
    """Renders the selected page based on authentication status."""
    render_top_navigation()
    st.markdown("<div class='content'>", unsafe_allow_html=True)
    st.markdown("<h1 class='title'>Vehicle Predictive Analysis Platform</h1>", unsafe_allow_html=True)

    if st.session_state.current_page == 'Home':
        show_home_page()
    elif not st.session_state.authenticated:
        if st.session_state.current_page == "Login":
            login.show_login_page(supabase)
        elif st.session_state.current_page == "Signup":
            login.show_signup_page(supabase)
        else:
            st.warning("Please log in to continue.")
    else:
        if st.session_state.current_page == "vehicle_form":
            vehicle_form.show_vehicle_form(supabase)
        elif st.session_state.current_page == "predictions":
            predictions.show_predictions(supabase)
        elif st.session_state.current_page == "llm_analysis":
            llm_analysis.show_llm_analysis(supabase)
        elif st.session_state.current_page == "update":
            update.show_vehicle_update_form(supabase)

if __name__ == "__main__":
    main()
