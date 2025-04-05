import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

# Configurar Streamlit para usar todo el ancho de la pantalla
st.set_page_config(layout="wide")

st.title("Subir ZIP y procesar archivos Excel más recientes")

uploaded_file = st.file_uploader("Sube un archivo ZIP", type="zip")

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Extraer ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Función para encontrar la carpeta raíz de una compañía
        def encontrar_carpeta_compania(nombre_compania):
            for root, dirs, files in os.walk(tmpdir):
                if os.path.basename(root).upper() == nombre_compania.upper():
                    return root
            return None

        # Función para cargar el Excel más reciente de una subcarpeta
        def cargar_excel_mas_reciente(carpeta_raiz, nombre_subcarpeta):
            if carpeta_raiz is None:
                return None, None
                
            for root, dirs, files in os.walk(carpeta_raiz):
                if os.path.basename(root).upper() == nombre_subcarpeta.upper():
                    archivos_excel = [
                        os.path.join(root, f) for f in files if f.endswith((".xlsx", ".xlsb"))
                    ]

                    if not archivos_excel:
                        return None, None
                    
                    archivo_mas_reciente = max(archivos_excel, key=os.path.getmtime)
                    
                    # Leer el archivo según su extensión
                    if archivo_mas_reciente.endswith(".xlsx"):
                        df = pd.read_excel(archivo_mas_reciente)
                    elif archivo_mas_reciente.endswith(".xlsb"):
                        with open_xlsb(archivo_mas_reciente) as wb:
                            df = pd.read_excel(wb)
                    
                    return df, archivo_mas_reciente
            return None, None

        # Función para cargar el archivo más reciente de PRODUCCIONTOTAL
        def cargar_produccion_total():
            carpeta_produccion = encontrar_carpeta_compania("PRODUCCIONTOTAL")
            if carpeta_produccion is None:
                return None, None
                
            archivos_excel = [
                os.path.join(carpeta_produccion, f) for f in os.listdir(carpeta_produccion) 
                if f.endswith((".xlsx", ".xlsb"))
            ]
            
            if not archivos_excel:
                return None, None
                
            archivo_mas_reciente = max(archivos_excel, key=os.path.getmtime)
            
            # Leer el archivo según su extensión y especificar la hoja
            if archivo_mas_reciente.endswith(".xlsx"):
                df = pd.read_excel(archivo_mas_reciente, sheet_name='Producción')
            elif archivo_mas_reciente.endswith(".xlsb"):
                with open_xlsb(archivo_mas_reciente) as wb:
                    df = pd.read_excel(wb, sheet_name='Producción')
            
            return df, archivo_mas_reciente

        # Función para convertir DataFrame a Excel
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format': '0.00'}) 
            worksheet.set_column('A:A', None, format1)  
            writer.close()
            processed_data = output.getvalue()
            return processed_data

        # Procesar archivos para cada compañía
        companias = ["COSNOR", "OCCIDENT", "REALE"]
        subcarpetas = ["CLIENTES", "POLIZAS", "RECIBOS"]
        
        # Diccionario para almacenar todos los DataFrames
        dataframes = {}
        
        # Crear un contenedor para la visualización
        st.subheader("Resumen de archivos encontrados")
        
        # Crear columnas para la visualización
        col1, col2, col3 = st.columns(3)
        
        # Procesar cada compañía
        for i, compania in enumerate(companias):
            carpeta_raiz = encontrar_carpeta_compania(compania)
            
            if carpeta_raiz is None:
                st.warning(f"No se encontró la carpeta '{compania}' dentro del ZIP.")
                continue
            
            # Seleccionar la columna según el índice
            col = col1 if i == 0 else (col2 if i == 1 else col3)
            
            with col:
                st.markdown(f"### {compania}")
                
                # Procesar cada subcarpeta
                for subcarpeta in subcarpetas:
                    df, archivo = cargar_excel_mas_reciente(carpeta_raiz, subcarpeta)
                    if df is not None:
                        nombre_df = f"df_{compania.lower()}_{subcarpeta.lower()}"
                        dataframes[nombre_df] = df
                        
                        # Mostrar información del archivo y el shape del DataFrame
                        st.markdown(f"**{subcarpeta}**")
                        st.markdown(f"📄 Archivo: `{os.path.basename(archivo)}`")
                        st.markdown(f"📊 Shape: `{df.shape[0]} filas × {df.shape[1]} columnas`")
                        
                        # Expander para ver el DataFrame
                        with st.expander(f"Ver datos de {subcarpeta}"):
                            st.dataframe(df)
                        
                        st.markdown("---")
        
        # Procesar PRODUCCIONTOTAL
        df_produccion, archivo_produccion = cargar_produccion_total()
        if df_produccion is not None:
            dataframes["df_produccion_total"] = df_produccion
            
            # Mostrar información de PRODUCCIONTOTAL
            st.markdown("### PRODUCCIONTOTAL")
            st.markdown(f"📄 Archivo: `{os.path.basename(archivo_produccion)}`")
            st.markdown(f"📊 Shape: `{df_produccion.shape[0]} filas × {df_produccion.shape[1]} columnas`")
            
            # Expander para ver el DataFrame de PRODUCCIONTOTAL
            with st.expander("Ver datos de PRODUCCIONTOTAL"):
                st.dataframe(df_produccion)
