import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import procesar_clientes_desde_polizas, procesar_polizas, procesarRecibos

def procesar_OCCIDENT():
    # Aplicar filtros
    st.session_state.df_origen_compañias['df_occident_polizas'] = st.session_state.df_origen_compañias['df_occident_polizas'][
        (st.session_state.df_origen_compañias['df_occident_polizas']['Situación de la póliza'].str.strip() == 'Vigor') & 
        (st.session_state.df_origen_compañias['df_occident_polizas']['Gestora'].isin(['M02811', 'M02771']))
    ]
    
    # Crea df Clientes
    compañia = "OCCIDENT"
    columna_cliente_poliza_origen = "Nombre del cliente"
    columna_cliente_clientes_origen = "Nombre completo"
    st.session_state.df_OCCIDENT['clientes'] = procesar_clientes_desde_polizas(compañia, st.session_state.df_origen_compañias['df_occident_polizas'], st.session_state.df_origen_compañias['df_occident_clientes'], st.session_state.df_OCCIDENT['clientes'], columna_cliente_poliza_origen, columna_cliente_clientes_origen)
    columna_id_polizas = "NIF"
    st.session_state.df_OCCIDENT['polizas'] = procesar_polizas(compañia, st.session_state.df_origen_compañias['df_occident_polizas'], st.session_state.df_origen_compañias['df_occident_clientes'], st.session_state.df_OCCIDENT['polizas'], columna_cliente_poliza_origen, columna_cliente_clientes_origen, columna_id_polizas)

    # Procesar recibos
    
    st.session_state.df_origen_compañias['df_occident_recibos'] = st.session_state.df_origen_compañias['df_occident_recibos']  [
        (st.session_state.df_origen_compañias['df_occident_recibos']['Agente'].str.strip() == 'M832793V') & 
        (st.session_state.df_origen_compañias['df_occident_recibos']['Situación del recibo'].isin(['Cobrado', 'Pendiente']))
    ]
    st.dataframe(st.session_state.df_origen_compañias['df_occident_recibos'])
    fecha_orden = "Fecha emisión";
    prima_orden = "Prima total";
    st.session_state.df_origen_compañias['df_occident_recibos'] = st.session_state.df_origen_compañias['df_occident_recibos'].sort_values(by=[fecha_orden, prima_orden], ascending=[False, False])
    st.session_state.df_OCCIDENT['recibos'] = procesarRecibos(compañia, st.session_state.df_OCCIDENT['recibos'], st.session_state.df_origen_compañias['df_occident_recibos'])
