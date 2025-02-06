import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

from components import login
from components import vehicle_form
from components import predictions
from components import llm_analysis
from components import update

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
        width: 100%;
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
    st.markdown("<div class='content'>", unsafe_allow_html=True)
    st.markdown("<h1 class='title'>Vehicle Predictive Analysis Platform</h1>", unsafe_allow_html=True)
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

    st.markdown("""
    <h2 class='section-title'>How it Works</h2>
    <p >Add all your vehicle data using the form. Regularly update your data to take full advantage of the predictive analysis and maintenance insights. The system will use machine learning models to predict the type of failure your vehicle may experience. Then, leveraging large language models (LLMs), it will provide detailed insights and suggestions for repair or maintenance.</p>
    <p style='text-align:center; color:#7f8c8d;'>Here's how the system operates:</p>
    <ol '>
        <li><strong>Machine Prioritization:</strong> This stage prioritizes vehicles for maintenance using a retrieval-augmented generation (RAG) system that processes both structured and unstructured data, including maintenance costs and past failures.</li>
        <li><strong>Failure Prediction:</strong> Vehicle sensor data is analyzed to predict failures using machine learning models, ensuring proactive maintenance.</li>
        <li><strong>Repair Plan Generation:</strong> Based on the predicted failures, the system generates detailed work orders with instructions and resource allocation using large language models (LLMs).</li>
        <li><strong>Maintenance Guidance:</strong> Generative AI integrates service notes and additional information into the repair plan, providing enhanced guidance to technicians during repairs.</li>
    </ol>
    <p s>By enhancing maintenance operations with AI, this platform offers substantial cost savings, improved efficiency, and heightened productivity, giving businesses a competitive edge.</p>
    """, unsafe_allow_html=True)
    
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


def render_sidebar_navigation():
    """Renders sidebar navigation based on authentication status."""
    with st.sidebar:
        if not st.session_state.authenticated:
            if st.button("Home"):
                st.session_state.current_page = "Home"
                st.experimental_rerun()
            if st.button("Login"):
                st.session_state.current_page = "Login"
                st.experimental_rerun()
            if st.button("Signup"):
                st.session_state.current_page = "Signup"
                st.experimental_rerun()
        else:
            if st.button("Vehicle Form"):
                st.session_state.current_page = "vehicle_form"
                st.experimental_rerun()
            if st.button("Predictions"):
                st.session_state.current_page = "predictions"
                st.experimental_rerun()
            if st.button("Analysis"):
                st.session_state.current_page = "llm_analysis"
                st.experimental_rerun()
            if st.button("Update"):
                st.session_state.current_page = "update"
                st.experimental_rerun()
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.current_page = "Home"
                st.success("✅ Logged out successfully!")
                st.experimental_rerun()


def main():
    """Renders the selected page based on authentication status."""
    render_sidebar_navigation()
    

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
