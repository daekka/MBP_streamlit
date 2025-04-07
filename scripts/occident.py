import streamlit as st
import pandas as pd
from scripts.lectura_datos_origen import procesar_clientes_desde_polizas, procesar_polizas, procesarRecibos
import datetime
import re
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
    columna_cp = "Código postal"
    columna_fnacimiento = "Fecha nacimiento"
    st.session_state.df_OCCIDENT['polizas'] = procesar_polizas(compañia, st.session_state.df_origen_compañias['df_occident_polizas'], st.session_state.df_origen_compañias['df_occident_clientes'], st.session_state.df_OCCIDENT['polizas'], columna_cliente_poliza_origen, columna_cliente_clientes_origen, columna_id_polizas, columna_cp, columna_fnacimiento)

    # Aplicar ambos filtros con la corrección
    st.session_state.df_origen_compañias['df_occident_recibos'] = st.session_state.df_origen_compañias['df_occident_recibos'][
        (st.session_state.df_origen_compañias['df_occident_recibos']['Agente'].str.strip() == 'M832793V') & 
        (st.session_state.df_origen_compañias['df_occident_recibos']['Situación del recibo'].str.strip().isin(['Cobrado', 'Pendiente']))
    ]
    
    fecha_orden = "Fecha emisión";
    prima_orden = "Prima total";
    st.session_state.df_origen_compañias['df_occident_recibos'] = st.session_state.df_origen_compañias['df_occident_recibos'].sort_values(by=[fecha_orden, prima_orden], ascending=[False, False])
    st.session_state.df_OCCIDENT['recibos'] = procesarRecibos(compañia, st.session_state.df_OCCIDENT['recibos'], st.session_state.df_origen_compañias['df_occident_recibos'])
    st.session_state.df_OCCIDENT['polizas'] = cubrir_polizas_con_datos_recibos_OCCIDENT(compañia, st.session_state.df_OCCIDENT['polizas'], st.session_state.df_OCCIDENT['recibos'], "N_POLIZA", "ID_Poliza");
    # Limpiar y formatear el domicilio de los clientes
    st.session_state.df_OCCIDENT['polizas'] = limpiar_y_formatear_OCCIDENT(st.session_state.df_OCCIDENT['polizas'])


def cubrir_polizas_con_datos_recibos_OCCIDENT_old(compañia, df_polizas, df_recibos, campo_id_poliza, campo_id_recibo):
    
    df_resultado = pd.DataFrame()  # Equivalente a df_plantilla_POLIZAS

    for i, poliza in df_polizas.iterrows():
        n_poliza = poliza[campo_id_poliza]
        if pd.isna(n_poliza):
            continue

        recibos_poliza = df_recibos[df_recibos[campo_id_recibo].astype(str) == str(n_poliza)].copy()
        recibos_poliza = recibos_poliza[['P_Neta', 'F_Remesa', 'Tipo_recibo', 'Periodicidad']]
        recibos_poliza = recibos_poliza.groupby('F_Remesa').agg({'P_Neta': 'sum', 'Tipo_recibo': 'first', 'Periodicidad': 'first'})

        if recibos_poliza.empty:
            prima = None
            primaanterior = None
            tipo_periodicidad = None
            prima_leida_ultimo_recibo = None
            periodo_leido_ultimo_recibo = None
        else:
            datos_unicos = {}
            for _, row in recibos_poliza.iterrows():
                fecha_key = pd.to_datetime(row['F_Remesa']).timestamp()
                if compañia == "OCCIDENT":
                    if fecha_key not in datos_unicos:
                        datos_unicos[fecha_key] = {
                            'fecha_efecto': pd.to_datetime(row['F_Remesa']),
                            'prima_neta': float(row['P_Neta']),
                            'esSuplemento': False,
                            'periodicidad': row['Periodicidad']
                        }
                    else:
                        datos_unicos[fecha_key]['prima_neta'] += float(row['P_Neta'])

            datos_normalizados = list(datos_unicos.values())
            st.write(datos_normalizados)
            if len(datos_normalizados) == 1:
                fecha_dato = datos_normalizados[0]['fecha_efecto']
                fecha_actual = pd.Timestamp.now()
                diff_meses = (fecha_actual.year - fecha_dato.year) * 12 + (fecha_actual.month - fecha_dato.month)

                if diff_meses > 6:
                    tipo_periodicidad = "Posible: Anual"
                elif diff_meses > 3:
                    tipo_periodicidad = "Posible: Anual / Semestral"
                elif diff_meses > 2:
                    tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral"
                elif diff_meses > 1:
                    tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral"
                elif diff_meses >= 1:
                    tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral / Mensual"
                else:
                    tipo_periodicidad = "indeterminado"

                prima = datos_normalizados[0]['prima_neta']
                primaanterior = None
                prima_leida_ultimo_recibo = prima
                periodo_leido_ultimo_recibo = datos_normalizados[0]['periodicidad']
            else:
                datos_normalizados.sort(key=lambda x: x['fecha_efecto'])

                def determinar_periodo(diff):
                    if diff <= 1.5: return 1
                    if diff <= 2.5: return 2
                    if diff <= 4: return 3
                    if diff <= 7: return 6
                    return 12

                diferencias = []
                for i in range(1, len(datos_normalizados)):
                    fecha_actual = datos_normalizados[i]['fecha_efecto']
                    fecha_anterior = datos_normalizados[i-1]['fecha_efecto']
                    diff = (fecha_actual.year - fecha_anterior.year) * 12 + (fecha_actual.month - fecha_anterior.month)
                    diferencias.append(diff)

                periodos_estandar = list(map(determinar_periodo, diferencias))
                conteo = pd.Series(periodos_estandar).value_counts()
                periodo_mas_comun = int(conteo.idxmax())

                tipo_periodicidad = {
                    1: "Mensual",
                    2: "Bimensual",
                    3: "Trimestral",
                    6: "Semestral",
                    12: "Anual"
                }.get(periodo_mas_comun, "Irregular")

                periodo_agrupacion = {
                    "Mensual": 12,
                    "Bimensual": 6,
                    "Trimestral": 4,
                    "Semestral": 2,
                    "Anual": 1
                }.get(tipo_periodicidad, 1)

                inicio = 0
                if compañia == "OCCIDENT" and len(datos_normalizados) > 1:
                    dias = [dato['fecha_efecto'].day for dato in datos_normalizados]
                    dia_mas_comun = pd.Series(dias).mode().iloc[0]
                    if datos_normalizados[0]['fecha_efecto'].day != dia_mas_comun:
                        inicio = 1

                primas_por_periodo = []
                for i in range(inicio, len(datos_normalizados), periodo_agrupacion):
                    grupo = datos_normalizados[i:i+periodo_agrupacion]
                    suma = sum(dato['prima_neta'] for dato in grupo)
                    if len(grupo) >= {
                        "Mensual": 12,
                        "Bimensual": 6,
                        "Trimestral": 4,
                        "Semestral": 2,
                        "Anual": 1
                    }.get(tipo_periodicidad, 1):
                        primas_por_periodo.append(suma)

                prima = primas_por_periodo[-1] if len(primas_por_periodo) >= 1 else None
                primaanterior = primas_por_periodo[-2] if len(primas_por_periodo) >= 2 else None
                prima_leida_ultimo_recibo = datos_normalizados[-1]['prima_neta']
                periodo_leido_ultimo_recibo = datos_normalizados[-1]['periodicidad']

        if periodo_leido_ultimo_recibo == "Anual":
            prima_leida_ultimo_recibo *= 1
        elif periodo_leido_ultimo_recibo == "Semestral":
            prima_leida_ultimo_recibo *= 2
        elif periodo_leido_ultimo_recibo == "Trimestral":
            prima_leida_ultimo_recibo *= 4
        elif periodo_leido_ultimo_recibo == "Bimensual":
            prima_leida_ultimo_recibo *= 6
        elif periodo_leido_ultimo_recibo == "Mensual":
            prima_leida_ultimo_recibo *= 12

        nueva_fila = {}
        for columna in df_polizas.columns:
            if columna == "PRIMA_NETA":
                nueva_fila[columna] = prima_leida_ultimo_recibo
            elif columna == "IMPORTE_ANO_ANTERIOR":
                nueva_fila[columna] = primaanterior if prima == prima_leida_ultimo_recibo else prima
            elif columna == "F_PAGO":
                if prima == prima_leida_ultimo_recibo:
                    nueva_fila[columna] = periodo_leido_ultimo_recibo
                else:
                    if periodo_leido_ultimo_recibo != tipo_periodicidad:
                        nueva_fila[columna] = f"¡Leída: {periodo_leido_ultimo_recibo}, Calculada: {tipo_periodicidad}"
                    else:
                        nueva_fila[columna] = periodo_leido_ultimo_recibo
            elif columna == "M_RENOVACION":
                fecha_renov = poliza.get('F_RENOVACION', None)
                if isinstance(fecha_renov, pd.Timestamp):
                    nueva_fila[columna] = fecha_renov.month
                else:
                    nueva_fila[columna] = None
            else:
                nueva_fila[columna] = poliza[columna]

        df_resultado = pd.concat([df_resultado, pd.DataFrame([nueva_fila])], ignore_index=True)

    return df_resultado



def cubrir_polizas_con_datos_recibos_OCCIDENT(compañia, df_polizas, df_recibos, campo_id_poliza, campo_id_recibo):
    
    df_resultado = pd.DataFrame()  # Equivalente a df_plantilla_POLIZAS

    for i, poliza in df_polizas.iterrows():
        n_poliza = poliza[campo_id_poliza]
        if pd.isna(n_poliza):
            continue

        recibos_poliza = df_recibos[df_recibos[campo_id_recibo].astype(str) == str(n_poliza)].copy()
        recibos_poliza = recibos_poliza[['P_Neta', 'F_Remesa', 'Tipo_recibo', 'Periodicidad']]
        #recibos_poliza = recibos_poliza.groupby('F_Remesa').agg({'P_Neta': 'sum'}).reset_index()
        #recibos_poliza = recibos_poliza.groupby('F_Remesa').agg({'P_Neta': 'sum', 'Tipo_recibo': 'first', 'Periodicidad': 'first'})

        if recibos_poliza.empty:
            prima_calculada = None
            primaanterior_calculada = None
            tipo_periodicidad = None
            periodo_calculada = None


        if recibos_poliza.shape[0] == 1:
            #st.write("Único recibo")
            fecha_dato = recibos_poliza['F_Remesa'].iloc[0]
            fecha_actual = pd.Timestamp.now()
            diff_meses = (fecha_actual - fecha_dato).days // 30

            if diff_meses > 6:
                tipo_periodicidad = "Posible: Anual"
            elif diff_meses > 3:
                tipo_periodicidad = "Posible: Anual / Semestral"
            elif diff_meses > 2:
                tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral"
            elif diff_meses > 1:
                tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral"
            elif diff_meses >= 1:
                tipo_periodicidad = "Posible: Anual / Semestral / Bimensual / Trimestral / Mensual"
            else:
                tipo_periodicidad = "indeterminado"
            #st.write(tipo_periodicidad)
            prima_calculada = recibos_poliza['P_Neta'].iloc[0]
            primaanterior_calculada = None
            periodo_calculada = tipo_periodicidad

        if recibos_poliza.shape[0] > 1:
            # Convertir el índice a una columna para poder trabajar con él
            #recibos_poliza = recibos_poliza.reset_index()
            #recibos_poliza['F_Remesa'] = pd.to_datetime(recibos_poliza['F_Remesa'])
            
            # Ordenamos por fecha
            recibos_poliza = recibos_poliza.sort_values(by=['F_Remesa'])

            # Calculamos la diferencia entre fechas
            recibos_poliza['diff_dias'] = recibos_poliza['F_Remesa'].diff().dt.days

            # Función para clasificar periodicidad según diferencia media
            def detectar_periodicidad(media_dias):
                if pd.isna(media_dias):
                    return 'Desconocido'
                if media_dias <= 40:
                    return 'Mensual'
                elif media_dias <= 75:
                    return 'Bimensual'
                elif media_dias <= 110:
                    return 'Trimestral'
                elif media_dias <= 200:
                    return 'Semestral'
                else:
                    return 'Anual'

            # Detectamos periodicidad para esta póliza
            media_dias = recibos_poliza['diff_dias'].mean()
            periodicidad_detectada = detectar_periodicidad(media_dias)
            
            # Añadimos la periodicidad detectada a cada fila
            recibos_poliza['Periodicidad_detectada'] = periodicidad_detectada

            # Agrupamos primas por período detectado
            # Cada agrupación depende de cuántos recibos componen el periodo
            periodo_map = {
                'Mensual': 12,
                'Bimensual': 6,
                'Trimestral': 4,
                'Semestral': 2,
                'Anual': 1
            }

            # Creamos grupos para esta póliza
            recibos_poliza['grupo'] = range(len(recibos_poliza))

            # Sumar primas agrupando por bloques del periodo
            recibos_poliza['bloque'] = recibos_poliza.apply(lambda row: row['grupo'] // periodo_map.get(periodicidad_detectada, 1), axis=1)

            # Contamos cuántos recibos hay en cada bloque
            conteo_por_bloque = recibos_poliza.groupby('bloque').size().reset_index(name='recibos_en_bloque')
            
            # Determinamos si cada bloque está completo
            recibos_esperados = periodo_map.get(periodicidad_detectada, 1)
            conteo_por_bloque['bloque_completo'] = conteo_por_bloque['recibos_en_bloque'] == recibos_esperados
            
            # Sumamos primas por grupo
            agrupado = recibos_poliza.groupby(['Periodicidad_detectada', 'bloque'])['P_Neta'].sum().reset_index()
            
            # Añadimos la información de bloques completos
            agrupado = agrupado.merge(conteo_por_bloque[['bloque', 'bloque_completo', 'recibos_en_bloque']], on='bloque')
            
            # Añadimos una columna que indique si el bloque está completo
            agrupado['estado_bloque'] = agrupado.apply(
                lambda row: f"Completo ({row['recibos_en_bloque']}/{recibos_esperados})" if row['bloque_completo'] 
                else f"Incompleto ({row['recibos_en_bloque']}/{recibos_esperados})", 
                axis=1
            )

            ultima_prima_completo = agrupado[agrupado['bloque_completo'] == True]['P_Neta'].iloc[-1]
            prima_calculada = ultima_prima_completo if not pd.isna(ultima_prima_completo) else 0
            primaanterior_calculada = agrupado[agrupado['bloque_completo'] == True]['P_Neta'].iloc[-2] if len(agrupado[agrupado['bloque_completo'] == True]) > 1 else None
            periodo_calculada = agrupado[agrupado['bloque_completo'] == True]['Periodicidad_detectada'].iloc[-1]



        pneta_ultimo_recibo = recibos_poliza['P_Neta'].iloc[-1]
        periodicidad_ultimo_recibo = recibos_poliza['Periodicidad'].iloc[-1]

        if periodicidad_ultimo_recibo == 'Anual':
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo * 1
        elif periodicidad_ultimo_recibo == 'Semestral':
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo * 2
        elif periodicidad_ultimo_recibo == 'Trimestral':
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo * 4
        elif periodicidad_ultimo_recibo == 'Bimensual':
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo * 6
        elif periodicidad_ultimo_recibo == 'Mensual':
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo * 12
        else:
            pneta_calculada_ultimo_recibo = pneta_ultimo_recibo
        
        

        df_polizas.loc[i, 'PRIMA_NETA'] = pneta_calculada_ultimo_recibo
        df_polizas.loc[i, 'IMPORTE_ANO_ANTERIOR'] = primaanterior_calculada if prima_calculada == pneta_calculada_ultimo_recibo else prima_calculada

        if pneta_calculada_ultimo_recibo == prima_calculada:
            df_polizas.loc[i, 'F_PAGO'] = periodicidad_ultimo_recibo
        else:
            if periodicidad_ultimo_recibo != periodo_calculada:
                df_polizas.loc[i, 'F_PAGO'] = f"¡Leída: {periodicidad_ultimo_recibo}, Calculada: {periodo_calculada}!"
            else:
                df_polizas.loc[i, 'F_PAGO'] = periodicidad_ultimo_recibo

        df_polizas.loc[i, 'M_RENOVACION'] = poliza['F_RENOVACION'].month if isinstance(poliza['F_RENOVACION'], datetime.date) else None
        df_polizas.loc[i, 'PRIMA_FRACCIONADA'] = recibos_poliza['P_Neta'].iloc[-1]
    return df_polizas

    
def limpiar_y_formatear_OCCIDENT(df):
    """
    domicilio = row['DOMICILIO']
    cp = str(row['C.P.'])
    localidad = row['LOCALIDAD'].upper()
    provincia = row['PROVINCIA'].upper()

    
    # Formatear piso y puerta
    match = re.search(r"piso:([^\s,]+)\s*puerta:([^\s,]*)", domicilio, flags=re.IGNORECASE)
    piso_puerta = ""
    if match:
        piso = match.group(1).strip()
        puerta = match.group(2).strip()
        piso_puerta = f"Piso {piso}"
        if puerta:
            piso_puerta += f", Puerta {puerta}"
        domicilio = re.sub(r"piso:[^\s,]+\s*puerta:[^\s,]*", piso_puerta, domicilio, flags=re.IGNORECASE)

    # Eliminar C.P., localidad y provincia
    domicilio = re.sub(rf",?\s*{cp}", "", domicilio)
    domicilio = re.sub(rf",?\s*{re.escape(localidad)}", "", domicilio, flags=re.IGNORECASE)
    domicilio = re.sub(rf",?\s*{re.escape(provincia)}", "", domicilio, flags=re.IGNORECASE)

    # Limpiar comas y espacios
    domicilio = re.sub(r",\s*,", ",", domicilio)
    domicilio = domicilio.strip(", ").strip()
    """
    df['RIESGO'] = df['RIESGO'].str.replace(r'^Código:\s+', '', regex=True)
    return df


        


