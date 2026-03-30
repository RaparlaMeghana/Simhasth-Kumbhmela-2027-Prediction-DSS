import ee
import streamlit as st

def init_gee():
    if "ee_initialized" not in st.session_state:
        try:
            ee.Initialize()
        except:
            ee.Authenticate()
            ee.Initialize()
        st.session_state.ee_initialized = True