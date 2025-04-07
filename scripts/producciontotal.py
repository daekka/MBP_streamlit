import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import procesar_clientes_desde_polizas, procesar_polizas, procesarRecibos

def procesar_PRODUCCIONTOTAL():

    # Crea df Clientes
    compañia = "PRODUCCIONTOTAL"
    columna_cliente_poliza_origen = "NOMBRE Y APELLIDOS"
    columna_cliente_clientes_origen = "NOMBRE Y APELLIDOS"
    st.session_state.df_PRODUCCIONTOTAL['clientes'] = procesar_clientes_desde_polizas(compañia, st.session_state.df_origen_compañias['df_produccion_total'], st.session_state.df_origen_compañias['df_produccion_total'], st.session_state.df_PRODUCCIONTOTAL['clientes'], columna_cliente_poliza_origen, columna_cliente_clientes_origen)
    
    columna_id_polizas = "DNI"
    columna_cp = "CP"
    columna_fnacimiento = "F. NACIMIENTO"
    st.session_state.df_PRODUCCIONTOTAL['polizas'] = procesar_polizas(compañia, st.session_state.df_origen_compañias['df_produccion_total'], st.session_state.df_origen_compañias['df_produccion_total'], st.session_state.df_PRODUCCIONTOTAL['polizas'], columna_cliente_poliza_origen, columna_cliente_clientes_origen, columna_id_polizas, columna_cp, columna_fnacimiento)
