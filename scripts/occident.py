import streamlit as st
import pandas as pd
def procesar_OCCIDENT():
    st.session_state.df_OCCIDENT['polizas'] = st.session_state.df_OCCIDENT['polizas'][(st.session_state.df_OCCIDENT['polizas']['Situación de la póliza'] == 'Vigor') & (st.session_state.df_OCCIDENT['polizas']['Gestora'].isin(['M02811', 'M02771']))]

