import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

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

        # Buscar la carpeta OCCIDENT
        occident_root = None
        for root, dirs, files in os.walk(tmpdir):
            if os.path.basename(root).upper() == "OCCIDENT":
                occident_root = root
                break

        if occident_root is None:
            st.error("No se encontró la carpeta 'OCCIDENT' dentro del ZIP.")
        else:
            def cargar_excel_mas_reciente(nombre_subcarpeta):
                for root, dirs, files in os.walk(occident_root):
                    if os.path.basename(root).upper() == nombre_subcarpeta.upper():
                        archivos_excel = [
                            os.path.join(root, f) for f in files if f.endswith(".xlsx")
                        ]

                        if not archivos_excel:
                            return None
                        archivo_mas_reciente = max(archivos_excel, key=os.path.getmtime)
                        st.text(archivo_mas_reciente)
                        return pd.read_excel(archivo_mas_reciente)
                return None

            # Cargar los Excel más recientes
            df_occident_clientes = cargar_excel_mas_reciente("CLIENTES")
            df_occident_polizas = cargar_excel_mas_reciente("POLIZAS")
            df_occident_recibos = cargar_excel_mas_reciente("RECIBOS")

            # Mostrar DataFrames si existen
            if df_occident_clientes is not None:
                st.subheader("Clientes - Excel más reciente")
                st.dataframe(df_occident_clientes)

            if df_occident_polizas is not None:
                st.subheader("Pólizas - Excel más reciente")
                st.dataframe(df_occident_polizas)

            if df_occident_recibos is not None:
                st.subheader("Recibos - Excel más reciente")
                st.dataframe(df_occident_recibos)
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
                df_xlsx = to_excel(df_occident_recibos)
                st.download_button(label='📥 Download Current Result',
                                                data=df_xlsx ,
                                                file_name= 'df_test.xlsx')
