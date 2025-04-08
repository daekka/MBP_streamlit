import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import procesar_clientes_desde_polizas, procesar_polizas, procesarRecibos

def procesar_renovaciones():

    # Recorrer todas las polizas
    compañia = "PRODUCCIONTOTAL"
    columna_id_polizas = "DNI"
    polizas = st.session_state.df_COMPLETO_POLIZAS['N_POLIZA']
    for index, poliza in polizas.iterrows():
        # Aquí puedes procesar cada poliza individualmente
        print(f"Poliza {index}: {poliza}")
