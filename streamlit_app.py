import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import abrir_zip_generara_df_compañias, leer_plantillas_tablas,crear_df_compañias_vacios, rellenar_datos_faltantes_con_PT, to_excel, formatear_campos_salidas
from scripts.occident import procesar_OCCIDENT
from scripts.producciontotal import procesar_PRODUCCIONTOTAL
import datetime


## Inicializar una variable si no existe
if 'df_origen_compañias' not in st.session_state:
    st.session_state.df_origen_compañias = {}
if 'df_plantillas_tablas' not in st.session_state:
    st.session_state.df_plantillas_tablas = {}
if 'df_OCCIDENT' not in st.session_state:
    st.session_state.df_OCCIDENT = {}
if 'df_PRODUCCIONTOTAL' not in st.session_state:
    st.session_state.df_PRODUCCIONTOTAL = {}
if 'df_COMPLETO_CLIENTES' not in st.session_state:
    st.session_state.df_COMPLETO_CLIENTES = {}
if 'df_COMPLETO_POLIZAS' not in st.session_state:
    st.session_state.df_COMPLETO_POLIZAS = {}

# Configurar Streamlit para usar todo el ancho de la pantalla
st.set_page_config(layout="wide")

st.title("MBP EVOLUTION - Integración de datos")

uploaded_file = st.file_uploader("Sube un archivo ZIP", type="zip")

if uploaded_file is not None: 
    st.divider()
    st.subheader("Leyendo archivos...", divider="rainbow")
    abrir_zip_generara_df_compañias(uploaded_file)
    leer_plantillas_tablas()
    crear_df_compañias_vacios()
    with st.expander("Detalles de los archivos cargados"):
        col1, col2, col3, col4 = st.columns(4)
        col1.header("OCCIDENT")
        col2.header("COSNOR")
        col3.header("REALE")
        col4.header("PRODUCCIONTOTAL")
        col1.metric(label="Fichero Pólizas OCCIDENT", value= st.session_state.df_origen_compañias['df_occident_polizas'].shape[0], border = True)
        col1.metric(label="Fichero Clientes OCCIDENT", value=st.session_state.df_origen_compañias['df_occident_clientes'].shape[0], border = True)
        col1.metric(label="Fichero Recibos OCCIDENT", value=st.session_state.df_origen_compañias['df_occident_recibos'].shape[0], border = True)
        col2.metric(label="Fichero Pólizas COSNOR", value= st.session_state.df_origen_compañias['df_cosnor_polizas'].shape[0], border = True)
        col2.metric(label="Fichero Clientes COSNOR", value=st.session_state.df_origen_compañias['df_cosnor_clientes'].shape[0], border = True)
        col2.metric(label="Fichero Recibos COSNOR", value=st.session_state.df_origen_compañias['df_cosnor_recibos'].shape[0], border = True)   
        col3.metric(label="Fichero Pólizas REALE", value= st.session_state.df_origen_compañias['df_reale_polizas'].shape[0], border = True)   
        col3.metric(label="Fichero Clientes REALE", value=st.session_state.df_origen_compañias['df_reale_clientes'].shape[0], border = True) 
        col3.metric(label="Fichero Recibos REALE", value=st.session_state.df_origen_compañias['df_reale_recibos'].shape[0], border = True) 
        col4.metric(label="Fichero Pólizas PRODUCCIONTOTAL", value= st.session_state.df_origen_compañias['df_produccion_total'].shape[0], border = True)  


    st.subheader("Procesando datos PRODUCCION TOTAL...", divider="green")
    procesar_PRODUCCIONTOTAL()
    with st.expander("Detalles de los clientes PRODUCCION TOTAL"):
        st.metric(label="Total de clientes PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['clientes'].shape[0], border = True)
        st.dataframe(st.session_state.df_PRODUCCIONTOTAL['clientes'])
    with st.expander("Detalles de las polizas PRODUCCION TOTAL"):
        st.metric(label="Total de polizas PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['polizas'].shape[0], border = True)
        st.dataframe(st.session_state.df_PRODUCCIONTOTAL['polizas'])


    st.subheader("Procesando datos OCCIDENT...", divider="red")
    procesar_OCCIDENT()
    with st.expander("Detalles de los clientes OCCIDENT"):
        st.metric(label="Total de clientes OCCIDENT", value=st.session_state.df_OCCIDENT['clientes'].shape[0], border = True)
        st.dataframe(st.session_state.df_OCCIDENT['clientes'])
    with st.expander("Detalles de las polizas OCCIDENT"):
        st.metric(label="Total de polizas OCCIDENT", value=st.session_state.df_OCCIDENT['polizas'].shape[0], border = True)
        st.dataframe(st.session_state.df_OCCIDENT['polizas'])
    with st.expander("Detalles de los recibos OCCIDENT"):
        st.metric(label="Total de recibos OCCIDENT", value=st.session_state.df_OCCIDENT['recibos'].shape[0], border = True)
        st.dataframe(st.session_state.df_OCCIDENT['recibos'])


    st.subheader("Rellenando datos con PRODUCCION TOTAL...", divider="orange")
    st.session_state.df_COMPLETO_CLIENTES = rellenar_datos_faltantes_con_PT(st.session_state.df_OCCIDENT['clientes'], st.session_state.df_PRODUCCIONTOTAL['clientes'], 'DNI')
    st.session_state.df_COMPLETO_POLIZAS = rellenar_datos_faltantes_con_PT(st.session_state.df_OCCIDENT['polizas'], st.session_state.df_PRODUCCIONTOTAL['polizas'], 'ID_DNI')
    with st.expander("Detalles de los clientes COMPLETOS"):
        st.metric(label="Total de clientes COMPLETOS", value=st.session_state.df_COMPLETO_CLIENTES.shape[0], border = True)
        st.dataframe(st.session_state.df_COMPLETO_CLIENTES)
    with st.expander("Detalles de las polizas COMPLETAS"):
        st.metric(label="Total de polizas COMPLETAS", value=st.session_state.df_COMPLETO_POLIZAS.shape[0], border = True)
        st.dataframe(st.session_state.df_COMPLETO_POLIZAS)

    st.session_state.df_COMPLETO_CLIENTES = formatear_campos_salidas(st.session_state.df_COMPLETO_CLIENTES)
    st.session_state.df_COMPLETO_POLIZAS = formatear_campos_salidas(st.session_state.df_COMPLETO_POLIZAS)

    # Guardar los datos completos en un archivo Excel
    with st.expander("Descargar datos completos"):
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.download_button(label="Descargar datos completos de clientes", data=to_excel(st.session_state.df_COMPLETO_CLIENTES), file_name=f"datos_completos_clientes_{fecha_actual}.xlsx")
        st.download_button(label="Descargar datos completos de polizas", data=to_excel(st.session_state.df_COMPLETO_POLIZAS), file_name=f"datos_completos_polizas_{fecha_actual}.xlsx")
        
    
