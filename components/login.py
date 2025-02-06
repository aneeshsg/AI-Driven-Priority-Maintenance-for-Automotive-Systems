import streamlit as st
from datetime import datetime

def show_login_page(supabase):
    st.header("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.write(response)
                st.session_state.authenticated = True
                st.session_state.user = response.user
                st.session_state.current_page = 'dashboard'
                
            except Exception as e:
                st.error(f"Invalid credentials: {str(e)}")

def show_signup_page(supabase):
    st.header("Sign Up")
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match")
                return
                
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("Account created successfully! Please login.")
                st.session_state.current_page = 'vehicle_form'
               
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")