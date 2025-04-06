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

def obtenerNombreColumnaConversion(plantilla, nombre_compania, nombre_campo):
    """
    Busca un dato en la columna 'Columna' y devuelve el valor correspondiente
    de la columna especificada por nombre_compania en la misma fila.

    Args:
        plantilla (pd.DataFrame): El DataFrame a analizar.
        nombre_compania (str): El nombre de la columna de la que se quiere obtener el valor.
        nombre_campo (Any): El valor que se desea buscar en la columna 'Columna'.

    Returns:
        Any: El valor correspondiente en la columna especificada por nombre_compania, o None si no se encuentra.
    """
    fila = plantilla[plantilla["Columna"] == nombre_campo]
    if not fila.empty:
        return fila.iloc[0][nombre_compania]
    else:
        return None
    
def procesar_clientes_desde_polizas(
    compania,
    df_polizas_compania,
    df_clientes_compania,
    df_plantilla,
    columna_cliente_poliza_origen,
    columna_cliente_clientes_origen,
):
    # Obtener el nombre de la columna de conversión
    clientes = df_polizas_compania[df_polizas_compania[columna_cliente_poliza_origen].notna()].drop_duplicates(subset=columna_cliente_poliza_origen)

    # Crear un DataFrame vacío para almacenar los resultados
    df_resultado = pd.DataFrame()
    
    for index, fila in clientes.iterrows():
        # Obtener el identificador del cliente
        id_cliente = fila[columna_cliente_poliza_origen]
        
        # Buscar el cliente en df_clientes_compania
        cliente_encontrado = df_clientes_compania[df_clientes_compania[columna_cliente_clientes_origen] == id_cliente]

        if not cliente_encontrado.empty:
            # Obtener la primera fila del cliente encontrado
            cliente_data = cliente_encontrado.iloc[0]

            # Crear un diccionario para almacenar los datos mapeados
            datos_mapeados = {}
            
            # Para cada columna en df_clientes_compania
            for columna_destino in df_plantilla.columns:
                # Buscar el nombre equivalente en la plantilla
                columna_origen = obtenerNombreColumnaConversion(
                    st.session_state.df_plantillas_tablas['clientes'], 
                    compania, 
                    columna_destino
                )

                # Si se encuentra un nombre equivalente y la columna existe en cliente_data, agregar el valor al diccionario
                if columna_origen is not None and columna_origen in cliente_data.index:
                    if isinstance(cliente_data[columna_origen], str):
                        datos_mapeados[columna_destino] = cliente_data[columna_origen].replace('\r\n', ' ')
                    else:
                        datos_mapeados[columna_destino] = cliente_data[columna_origen]
            # Agregar los datos mapeados al DataFrame resultado
            df_resultado = pd.concat([df_resultado, pd.DataFrame([datos_mapeados])], ignore_index=True)
        else:
            # Si no se encuentra el cliente, mostrar un mensaje de advertencia
            nombre_cliente = fila[columna_cliente_poliza_origen]
            mensaje_advertencia = f"ADVERTENCIA: Hay una póliza en vigor a nombre de '{nombre_cliente}' que no se encontró en los datos de clientes."
            st.write(mensaje_advertencia)
            print (mensaje_advertencia)

    df_resultado['GRUPO_ASEGURADOR'] = compania
    return df_resultado



def procesar_polizas(
    compania,
    dfPolizasCompania,
    dfClientesCompania,
    dfPlantilla,
    columnaClientePolizaOrigen,
    columnaClienteClientesOrigen,
    columnaIDPolizas
):
    df_resultado = dfPlantilla

    for index, poliza in dfPolizasCompania.iterrows():
        # Crear un diccionario para almacenar los datos mapeados
        datos_mapeados = {}
                    
        # Para cada columna en df_clientes_compania
        for columna_destino in dfPlantilla.columns:
            # Buscar el nombre equivalente en la plantilla
            columna_origen = obtenerNombreColumnaConversion(
                st.session_state.df_plantillas_tablas['polizas'], 
                compania, 
                columna_destino
            )

            # Si se encuentra un nombre equivalente y la columna existe en cliente_data, agregar el valor al diccionario
            if columna_origen is not None and not pd.isna(columna_origen) and columna_origen not in datos_mapeados:
                datos_mapeados[columna_destino] = poliza[columna_origen]

        # Buscar en dfClientesCompania por columna_cliente_clientes_origen el campo columna_id_polizas
        cliente_encontrado = dfClientesCompania[dfClientesCompania[columnaClienteClientesOrigen] == poliza[columnaClientePolizaOrigen]]

        if not cliente_encontrado.empty:
            datos_mapeados['ID_DNI'] = cliente_encontrado[columnaIDPolizas].values[0]
            datos_mapeados['CLIENTE'] = cliente_encontrado[columnaClienteClientesOrigen].values[0]
        
        datos_mapeados['GRUPO_ASEGURADOR'] = compania
        # Agregar los datos mapeados al DataFrame resultado
        df_resultado = pd.concat([df_resultado, pd.DataFrame([datos_mapeados])], ignore_index=True)

    return df_resultado


def procesarRecibos(compania, df_plantilla_RECIBOS, df_origen_recibos):
    df_resultado = df_plantilla_RECIBOS

    for index, recibo in df_origen_recibos.iterrows():
        # Crear un diccionario para almacenar los datos mapeados
        datos_mapeados = {}
                    
        # Para cada columna en df_clientes_compania
        for columna_destino in df_plantilla_RECIBOS.columns:
            # Buscar el nombre equivalente en la plantilla
            columna_origen = obtenerNombreColumnaConversion(
                st.session_state.df_plantillas_tablas['polizas'], 
                compania, 
                columna_destino
            )

            # Si se encuentra un nombre equivalente y la columna existe en cliente_data, agregar el valor al diccionario
            if columna_origen is not None and not pd.isna(columna_origen) and columna_origen not in datos_mapeados:
                datos_mapeados[columna_destino] = recibo[columna_origen]
        
        datos_mapeados['GRUPO_ASEGURADOR'] = compania

        # Agregar los datos mapeados al DataFrame resultado
        df_resultado = pd.concat([df_resultado, pd.DataFrame([datos_mapeados])], ignore_index=True)

    return df_resultado
