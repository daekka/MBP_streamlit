import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import abrir_zip_generara_df_compañias, leer_plantillas_tablas,crear_df_compañias_vacios, rellenar_datos_faltantes_con_PT, to_excel, descargar_ficheros_completos, mapeado_resultado_final    
from scripts.occident import procesar_OCCIDENT
from scripts.producciontotal import procesar_PRODUCCIONTOTAL
import datetime
from io import BytesIO
import base64


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
if 'df_renovaciones' not in st.session_state:
    st.session_state.df_renovaciones = pd.DataFrame()
if 'df_fusion' not in st.session_state:
    st.session_state.df_fusion = pd.DataFrame()

# Configurar Streamlit para usar todo el ancho de la pantalla
st.set_page_config(layout="wide")

st.title("MBP EVOLUTION - Integración de datos")
# Toggle para activar los logs
logs_activados = st.checkbox("¿Activar los logs?", value=False)


# Subir el primer archivo (obligatorio)
uploaded_file_1 = st.file_uploader("Sube el fichero ZIP con los datos de las compañias (obligatorio)", type="zip", accept_multiple_files=False)

# Switch para habilitar o no el segundo archivo
second_file_required = st.checkbox("¿Quieres subir el fichero de trabajo para fusionar información?", value=True)

# Subir el segundo archivo solo si se activa el checkbox
if second_file_required:
    uploaded_file_2 = st.file_uploader("Sube el archivo de trabajo para fusionar información (opcional)", type="xlsx", accept_multiple_files=False)
else:
    uploaded_file_2 = None

# Verificar que el primer archivo esté cargado
if uploaded_file_1 is not None:
    st.write("Fichero datos compañias cargado correctamente:", uploaded_file_1.name)
    
    # Si se requiere el segundo archivo, verificar que esté cargado
    if second_file_required and uploaded_file_2 is None:
        st.warning("Por favor, sube el fichero de trabajo para fusionar información.")
    elif second_file_required and uploaded_file_2 is not None:
        st.write("Fichero de trabajo cargado correctamente:", uploaded_file_2.name)
    
    # Procesar solo si el primer archivo está cargado y el segundo (si es requerido) también
    if not second_file_required or (second_file_required and uploaded_file_2 is not None):
        st.divider()
        st.subheader("Leyendo archivos...", divider="rainbow")

        # Leer el archivo de fusión
        if uploaded_file_2 is not None:
            st.session_state.df_fusion = pd.read_excel(uploaded_file_2)

        # Procesar el primer archivo
        abrir_zip_generara_df_compañias(uploaded_file_1)
        
        # Si hay un segundo archivo, procesarlo también
        if second_file_required and uploaded_file_2 is not None:
            # Aquí puedes agregar la lógica para procesar el segundo archivo
            # Por ejemplo, podrías tener una función específica para el segundo archivo
            # o combinar los datos de ambos archivos
            st.info("Procesando el segundo archivo...")
            # Ejemplo: procesar_segundo_archivo(uploaded_file_2)
        
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
        if logs_activados:
            with st.expander("Detalles de los clientes PRODUCCION TOTAL"):
                st.metric(label="Total de clientes PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['clientes'].shape[0], border = True)
                st.dataframe(st.session_state.df_PRODUCCIONTOTAL['clientes'])

            with st.expander("Detalles de las polizas PRODUCCION TOTAL"):
                st.metric(label="Total de polizas PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['polizas'].shape[0], border = True)
                st.dataframe(st.session_state.df_PRODUCCIONTOTAL['polizas'])


        st.subheader("Procesando datos OCCIDENT...", divider="red")
        procesar_OCCIDENT()
        
        if logs_activados:
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
        st.session_state.df_COMPLETO_POLIZAS = rellenar_datos_faltantes_con_PT(st.session_state.df_OCCIDENT['polizas'], st.session_state.df_PRODUCCIONTOTAL['polizas'], 'N_POLIZA')
        if logs_activados:
            with st.expander("Detalles de los clientes COMPLETOS"):
                st.metric(label="Total de clientes COMPLETOS", value=st.session_state.df_COMPLETO_CLIENTES.shape[0], border = True)
                st.dataframe(st.session_state.df_COMPLETO_CLIENTES)
            with st.expander("Detalles de las polizas COMPLETAS"):
                st.metric(label="Total de polizas COMPLETAS", value=st.session_state.df_COMPLETO_POLIZAS.shape[0], border = True)
                st.dataframe(st.session_state.df_COMPLETO_POLIZAS)

        st.session_state.df_COMPLETO_POLIZAS = mapeado_resultado_final(st.session_state.df_COMPLETO_POLIZAS)

        
        # Mapear los datos completos
        if uploaded_file_2 is not None:
            st.session_state.df_COMPLETO_POLIZAS = rellenar_datos_faltantes_con_PT(st.session_state.df_COMPLETO_POLIZAS, st.session_state.df_fusion, 'N_POLIZA')

        st.balloons()
        
        st.subheader("Proceso finalizado: datos completos...", divider="rainbow")
        # Guardar los datos completos en un archivo Excel
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with BytesIO() as output_clientes:
            writer_clientes = pd.ExcelWriter(output_clientes, engine='xlsxwriter')
            st.session_state.df_COMPLETO_CLIENTES.to_excel(writer_clientes, sheet_name='Clientes')
            writer_clientes.book.close()
            st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(output_clientes.getvalue()).decode()}' download='datos_completos_clientes_{fecha_actual}.xlsx' style='font-size: 20px; text-decoration: underline;'>Descargar datos completos de clientes</a>", unsafe_allow_html=True)

        with BytesIO() as output_polizas:
            writer_polizas = pd.ExcelWriter(output_polizas, engine='xlsxwriter')
            st.session_state.df_COMPLETO_POLIZAS.to_excel(writer_polizas, sheet_name='Polizas')
            writer_polizas.book.close()
            st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(output_polizas.getvalue()).decode()}' download='datos_completos_polizas_{fecha_actual}.xlsx' style='font-size: 20px; text-decoration: underline;'>Descargar datos completos de polizas</a>", unsafe_allow_html=True)

else:
    st.warning("Por favor, sube el fichero ZIP con los datos de las compañias.")

