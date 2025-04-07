import streamlit as st

# Subir el primer archivo (obligatorio)
uploaded_file_1 = st.file_uploader("Selecciona el primer archivo (obligatorio)", type=["csv", "txt", "jpg", "png"])

# Switch para habilitar o no el segundo archivo
second_file_required = st.checkbox("¿Quieres subir un segundo archivo?", value=False)

# Subir el segundo archivo solo si se activa el checkbox
if second_file_required:
    uploaded_file_2 = st.file_uploader("Selecciona el segundo archivo (opcional)", type=["csv", "txt", "jpg", "png"])
else:
    uploaded_file_2 = None

# Verificar que ambos archivos (el primero y el segundo si se activa el switch) estén cargados
if uploaded_file_1 is not None:
    st.write("Primer archivo cargado correctamente:")
    st.write(uploaded_file_1.name)
else:
    st.write("Por favor, sube el primer archivo.")

if second_file_required and uploaded_file_2 is not None:
    st.write("Segundo archivo cargado correctamente:")
    st.write(uploaded_file_2.name)

# Procesar solo si ambos archivos están cargados correctamente
if uploaded_file_1 is not None and (not second_file_required or uploaded_file_2 is not None):
    # Código común para procesar los archivos después de que ambos se hayan cargado
    st.write("Comienza proceso")
    # Aquí iría tu lógica para procesar los archivos
else:
    if second_file_required and uploaded_file_2 is None:
        st.write("Por favor, sube el segundo archivo.")
