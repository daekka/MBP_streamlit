import zipfile
import tempfile
import os
from io import BytesIO
import pandas as pd
from pyxlsb import open_workbook as open_xlsb
import streamlit as st

# Configuración de sheets y headers por compañía
CONFIG_EXCEL = {
    "PRODUCCIONTOTAL": {
        "sheet": "Producción",
        "headerRow": 0
    },
    "default": {
        "CLIENTES": {"sheet": 0, "headerRow": 0},
        "POLIZAS": {"sheet": 0, "headerRow": 0},
        "RECIBOS": {"sheet": 0, "headerRow": 0}
    },
    "COSNOR": {
        "CLIENTES": {"sheet": 0, "headerRow": 1},
        "POLIZAS": {"sheet": 0, "headerRow": 1},
        "RECIBOS": {"sheet": 0, "headerRow": 1}
    },
    "OCCIDENT": {
        "CLIENTES": {"sheet": 0, "headerRow": 0},
        "POLIZAS": {"sheet": 0, "headerRow": 0},
        "RECIBOS": {"sheet": 0, "headerRow": 0}
    },
    "REALE": {
        "CLIENTES": {"sheet": 0, "headerRow": 0},
        "POLIZAS": {"sheet": 0, "headerRow": 0},
        "RECIBOS": {"sheet": 0, "headerRow": 0}
    }
}

def abrir_zip_generara_df_compañias(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Descargar el archivo zip
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        # Extraer ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Generar el dataframe de COSNOR
        procesar_compañias(tmpdir)

# Función para encontrar la carpeta raíz de una compañía
def encontrar_carpeta_compania(nombre_compania, tmpdir):
    for root, dirs, files in os.walk(tmpdir):
        if os.path.basename(root).upper() == nombre_compania.upper():
            return root
    return None

# Función para cargar el Excel más reciente de una subcarpeta
def cargar_excel_mas_reciente(carpeta_raiz, nombre_subcarpeta, compania):
    if carpeta_raiz is None:
        return None, None
        
    for root, dirs, files in os.walk(carpeta_raiz):
        if os.path.basename(root).upper() == nombre_subcarpeta.upper():
            archivos_excel = [
                os.path.join(root, f) for f in files if f.endswith((".xlsx", ".xlsb"))
            ]

            if not archivos_excel:
                df = pd.DataFrame()  # Crear DataFrame vacío si no hay archivos
                return df, None
            
            archivo_mas_reciente = max(archivos_excel, key=os.path.getmtime)
            
            # Obtener configuración específica o usar la configuración por defecto
            config = CONFIG_EXCEL.get(compania, CONFIG_EXCEL["default"])
            subcarpeta_config = config.get(nombre_subcarpeta, CONFIG_EXCEL["default"][nombre_subcarpeta])
            
            # Leer el archivo según su extensión
            if archivo_mas_reciente.endswith(".xlsx"):
                df = pd.read_excel(
                    archivo_mas_reciente,
                    sheet_name=subcarpeta_config["sheet"],
                    header=subcarpeta_config["headerRow"]
                )
            elif archivo_mas_reciente.endswith(".xlsb"):
                with open_xlsb(archivo_mas_reciente) as wb:
                    df = pd.read_excel(
                        wb,
                        sheet_name=subcarpeta_config["sheet"],
                        header=subcarpeta_config["headerRow"]
                    )
            
            return df, archivo_mas_reciente
    return None, None

# Función para cargar el archivo más reciente de PRODUCCIONTOTAL
def cargar_produccion_total(tmpdir):
    carpeta_produccion = encontrar_carpeta_compania("PRODUCCIONTOTAL", tmpdir)
    if carpeta_produccion is None:
        return None, None
        
    archivos_excel = [
        os.path.join(carpeta_produccion, f) for f in os.listdir(carpeta_produccion) 
        if f.endswith((".xlsx", ".xlsb"))
    ]
    
    if not archivos_excel:
        return None, None
        
    archivo_mas_reciente = max(archivos_excel, key=os.path.getmtime)
    
    # Obtener configuración específica para PRODUCCIONTOTAL
    config = CONFIG_EXCEL["PRODUCCIONTOTAL"]
    
    # Leer el archivo según su extensión y especificar la hoja
    if archivo_mas_reciente.endswith(".xlsx"):
        df = pd.read_excel(
            archivo_mas_reciente,
            sheet_name=config["sheet"],
            header=config["headerRow"]
        )
    elif archivo_mas_reciente.endswith(".xlsb"):
        with open_xlsb(archivo_mas_reciente) as wb:
            df = pd.read_excel(
                wb,
                sheet_name=config["sheet"],
                header=config["headerRow"]
            )
    
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


def procesar_compañias(tmpdir):
    # Procesar archivos para cada compañía
    companias = ["COSNOR", "OCCIDENT", "REALE"]
    subcarpetas = ["CLIENTES", "POLIZAS", "RECIBOS"]
         
    # Procesar cada compañía
    for i, compania in enumerate(companias):
        #st.write("Leyendo compañia: ", compania)
        carpeta_raiz = encontrar_carpeta_compania(compania, tmpdir)
        
        # Procesar cada subcarpeta
        for subcarpeta in subcarpetas:
            nombre_df = f"df_{compania.lower()}_{subcarpeta.lower()}"
            
            if carpeta_raiz is None:
                # Si no se encuentra la carpeta de la compañía, crear DataFrame vacío
                st.session_state.df_origen_compañias[nombre_df] = pd.DataFrame()
            else:
                df, archivo = cargar_excel_mas_reciente(carpeta_raiz, subcarpeta, compania)
                # Si no se encuentra el archivo o hay algún problema, crear DataFrame vacío
                if df is None:
                    st.session_state.df_origen_compañias[nombre_df] = pd.DataFrame()
                else:
                    # Actualizar el DataFrame existente
                    st.session_state.df_origen_compañias[nombre_df] = df
    
    # Procesar PRODUCCIONTOTAL
    df_produccion, archivo_produccion = cargar_produccion_total(tmpdir)
    if df_produccion is not None:
        st.session_state.df_origen_compañias["df_produccion_total"] = df_produccion
    else:
        # Si no se encuentra el archivo de producción total, crear DataFrame vacío
        st.session_state.df_origen_compañias["df_produccion_total"] = pd.DataFrame()


def crear_df_vacio_desde_plantilla(df_plantilla):
    # Extraer los valores de la columna 'Columna' (ignorando los vacíos o nulos)
    columnas = df_plantilla['Columna'].dropna().tolist()
    # Crear un DataFrame vacío con esas columnas
    df_vacio = pd.DataFrame(columns=columnas)
    return df_vacio


def leer_plantillas_tablas():
    st.session_state.df_plantillas_tablas['clientes'] = pd.read_excel("tablas_origen\\tablas_conversion_clientes.xlsx")
    st.session_state.df_plantillas_tablas['polizas'] = pd.read_excel("tablas_origen\\tablas_conversion_polizas.xlsx")
    st.session_state.df_plantillas_tablas['recibos'] = pd.read_excel("tablas_origen\\tablas_conversion_recibos.xlsx")

def crear_df_vacio_desde_plantilla(df_original):
    # Extraer los valores de la columna 'Columna' (ignorando los vacíos o nulos)
    columnas = df_original['Columna'].dropna().tolist()
    # Crear un DataFrame vacío con esas columnas
    df_vacio = pd.DataFrame(columns=columnas)
    return df_vacio

def crear_df_compañias_vacios():
    st.session_state.df_OCCIDENT['clientes'] = crear_df_vacio_desde_plantilla(st.session_state.df_plantillas_tablas['clientes'])
    st.session_state.df_OCCIDENT['polizas'] = crear_df_vacio_desde_plantilla(st.session_state.df_plantillas_tablas['polizas'])
    st.session_state.df_OCCIDENT['recibos'] = crear_df_vacio_desde_plantilla(st.session_state.df_plantillas_tablas['recibos'])

