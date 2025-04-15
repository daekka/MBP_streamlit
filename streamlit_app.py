import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import abrir_zip_generara_df_compañias, leer_plantillas_tablas,crear_df_compañias_vacios, rellenar_datos_faltantes_con_PT, to_excel, descargar_ficheros_completos, mapeado_resultado_final    
from scripts.occident import procesar_OCCIDENT
from scripts.producciontotal import procesar_PRODUCCIONTOTAL
import datetime
import pytz
from io import BytesIO
import base64
import pytz

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
if 'mostrar_ayuda' not in st.session_state:
    st.session_state.mostrar_ayuda = False

# Configurar Streamlit para usar todo el ancho de la pantalla y mostrar el logo de MBP
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_icon="assets\logo_mbp.png")

#st.logo("assets/logo_mbp.png", size="large")


# Aplicar CSS personalizado para hacer el menú lateral más ancho
st.markdown("""
<style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 350px;
        max-width: 350px;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar el archivo HTML de ayuda
def cargar_ayuda_html():
    with open('ayuda.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

# Crear una barra lateral para la ayuda y configuración
with st.sidebar:
    st.title("INTEGRACIÓN DE DATOS")
    st.markdown("## 📚 Ayuda")
    if st.button("Ver documentación", help="Muestra la documentación de ayuda de la aplicación"):
        st.session_state.mostrar_ayuda = True
    
    st.markdown("---")
    st.markdown("## ⚙️ Configuración")
    # Mover el checkbox de second_file_required al menú lateral
    second_file_required = st.checkbox("¿Quieres subir el fichero de trabajo para fusionar información?", value=True, help="Activa la opción para subir un archivo adicional para fusionar información")
    
    # Mover el checkbox de logs al menú lateral
    logs_activados = st.checkbox("Activar logs", value=False, help="Muestra información detallada durante el procesamiento de datos")
    
    st.markdown("---")
    st.markdown("### Acerca de")
    st.markdown("## MBP EVOLUTION")
    st.markdown("Integración de datos")
    st.markdown("Versión 0.1")

# Mostrar la ayuda si el botón fue presionado
if st.session_state.mostrar_ayuda:
    ayuda_html = cargar_ayuda_html()
    st.components.v1.html(ayuda_html, height=800, scrolling=True)
    
    # Botón para cerrar la ayuda
    if st.button("❌ Cerrar Ayuda"):
        st.session_state.mostrar_ayuda = False
        st.experimental_rerun()

st.title("MBP EVOLUTION - Integración de datos")

# Subir el primer archivo (obligatorio)
uploaded_file_1 = st.file_uploader("Sube el fichero ZIP con los datos de las compañias (obligatorio)", type="zip", accept_multiple_files=False)

# Subir el segundo archivo solo si se activa el checkbox
if second_file_required:
    uploaded_file_2 = st.file_uploader("Sube el archivo de trabajo para fusionar información (opcional)", type="xlsx", accept_multiple_files=False)
else:
    uploaded_file_2 = None

# Verificar que el primer archivo esté cargado
if uploaded_file_1 is not None:
    #st.write("Fichero datos compañias cargado correctamente:", uploaded_file_1.name)
    
    # Si se requiere el segundo archivo, verificar que esté cargado
    if second_file_required and uploaded_file_2 is None:
        st.warning("Por favor, sube el fichero de trabajo para fusionar información.")
    elif second_file_required and uploaded_file_2 is not None:
        #st.write("Fichero de trabajo cargado correctamente:", uploaded_file_2.name)
        print("Fichero de trabajo cargado correctamente:", uploaded_file_2.name)
    
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
            # st.info("Procesando el segundo archivo...")
            # Ejemplo: procesar_segundo_archivo(uploaded_file_2)
            print("Procesando el segundo archivo...")

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
        with st.expander("Detalles de los datos PRODUCCION TOTAL"):
            col1, col2 = st.columns(2)
            col1.header("CLIENTES")
            col2.header("PÓLIZAS")
            col1.metric(label="Fichero Clientes PRODUCCION TOTAL", value= st.session_state.df_PRODUCCIONTOTAL['clientes']['DNI'].nunique(), border = True)
            col2.metric(label="Fichero Pólizas PRODUCCION TOTAL", value= st.session_state.df_PRODUCCIONTOTAL['polizas']['N_POLIZA'].nunique(), border = True)

        if logs_activados:
            with st.expander("Detalles de los clientes PRODUCCION TOTAL"):
                st.metric(label="Total de clientes PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['clientes'].shape[0], border = True)
                st.dataframe(st.session_state.df_PRODUCCIONTOTAL['clientes'])

            with st.expander("Detalles de las polizas PRODUCCION TOTAL"):
                st.metric(label="Total de polizas PRODUCCION TOTAL", value=st.session_state.df_PRODUCCIONTOTAL['polizas'].shape[0], border = True)
                st.dataframe(st.session_state.df_PRODUCCIONTOTAL['polizas'])


        st.subheader("Procesando datos OCCIDENT...", divider="red")
        procesar_OCCIDENT()
        with st.expander("Detalles de los datos OCCIDENT"):
            col1, col2 = st.columns(2)
            col1.header("CLIENTES")
            col2.header("PÓLIZAS")
            col1.metric(label="Fichero Clientes OCCIDENT", value= st.session_state.df_OCCIDENT['clientes']['DNI'].nunique(), border = True)
            col2.metric(label="Fichero Pólizas OCCIDENT", value= st.session_state.df_OCCIDENT['polizas']['N_POLIZA'].nunique(), border = True)

        
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

        st.subheader("Rellenando datos faltantes con PRODUCCION TOTAL...", divider="orange")
        st.session_state.df_COMPLETO_CLIENTES = rellenar_datos_faltantes_con_PT(st.session_state.df_OCCIDENT['clientes'], st.session_state.df_PRODUCCIONTOTAL['clientes'], 'DNI')
        st.session_state.df_COMPLETO_POLIZAS = rellenar_datos_faltantes_con_PT(st.session_state.df_OCCIDENT['polizas'], st.session_state.df_PRODUCCIONTOTAL['polizas'], 'N_POLIZA')
        
        if logs_activados:
            with st.expander("Detalles de los clientes COMPLETOS"):
                st.metric(label="Total de clientes COMPLETOS", value=st.session_state.df_COMPLETO_CLIENTES.shape[0], border = True)
                st.dataframe(st.session_state.df_COMPLETO_CLIENTES)
            with st.expander("Detalles de las polizas COMPLETAS"):
                st.metric(label="Total de polizas COMPLETAS", value=st.session_state.df_COMPLETO_POLIZAS.shape[0], border = True)
                st.dataframe(st.session_state.df_COMPLETO_POLIZAS)
      
        # Mapear los datos completos
        st.session_state.df_COMPLETO_POLIZAS = mapeado_resultado_final(st.session_state.df_COMPLETO_POLIZAS)

        
        # Mapear los datos completos
        if uploaded_file_2 is not None:
            st.session_state.df_COMPLETO_POLIZAS = rellenar_datos_faltantes_con_PT(st.session_state.df_COMPLETO_POLIZAS, st.session_state.df_fusion, 'N_POLIZA')

        st.balloons()
        
        st.subheader("Proceso finalizado: datos completos...", divider="rainbow")
        with st.expander("Detalles de los datos finales"):
            col1, col2 = st.columns(2)
            col1.header("CLIENTES")
            col2.header("PÓLIZAS")
            col1.metric(label="Fichero Clientes finales", value= st.session_state.df_COMPLETO_CLIENTES['DNI'].nunique(), border = True)
            col2.metric(label="Fichero Pólizas finales", value= st.session_state.df_COMPLETO_POLIZAS['N_POLIZA'].nunique(), border = True)
            df_clientes_por_compania = pd.DataFrame({
                "Compañía": ["OCCIDENT", "REALE", "COSNOR", "TOTAL"],
                "Cantidad de Clientes": [
                    st.session_state.df_OCCIDENT['clientes'].shape[0],
                    0,
                    0,
                    st.session_state.df_OCCIDENT['clientes'].shape[0]
                ]
            })
            
            # Crear un gráfico de barras usando la función nativa de Streamlit
            # Configurar el gráfico para mostrar cada compañía con un color específico
            col1.bar_chart(
                df_clientes_por_compania.set_index('Compañía'),
                use_container_width=True,
                        )
            
            df_polizas_por_compania = pd.DataFrame({
                "Compañía": ["OCCIDENT", "REALE", "COSNOR", "TOTAL"],
                "Cantidad de Pólizas": [
                    st.session_state.df_OCCIDENT['polizas'].shape[0],
                    0,
                    0,
                    st.session_state.df_OCCIDENT['polizas'].shape[0]
                ]
            })
            
            # Crear un gráfico de barras usando la función nativa de Streamlit
            # Configurar el gráfico para mostrar cada compañía con un color específico
            col2.bar_chart(
                df_polizas_por_compania.set_index('Compañía'),
                use_container_width=True,
                        )

        # Guardar los datos completos en un archivo Excel
        madrid_tz = pytz.timezone('Europe/Madrid')
        fecha_actual = datetime.datetime.now(madrid_tz).strftime("%Y-%m-%d_%H-%M-%S")
        with BytesIO() as output_clientes:
            writer_clientes = pd.ExcelWriter(output_clientes, engine='xlsxwriter')
            st.session_state.df_COMPLETO_CLIENTES.to_excel(writer_clientes, sheet_name='Clientes', index=False)
            writer_clientes.book.close()
            st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(output_clientes.getvalue()).decode()}' download='datos_completos_clientes_{fecha_actual}.xlsx' style='font-size: 20px; text-decoration: underline;'>Descargar datos completos de clientes</a>", unsafe_allow_html=True)

        with BytesIO() as output_polizas:
            writer_polizas = pd.ExcelWriter(output_polizas, engine='xlsxwriter')
            st.session_state.df_COMPLETO_POLIZAS.to_excel(writer_polizas, sheet_name='Polizas', index=False)
            writer_polizas.book.close()
            st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(output_polizas.getvalue()).decode()}' download='datos_completos_polizas_{fecha_actual}.xlsx' style='font-size: 20px; text-decoration: underline;'>Descargar datos completos de polizas</a>", unsafe_allow_html=True)

else:
    st.warning("Por favor, sube el fichero ZIP con los datos de las compañias.")

