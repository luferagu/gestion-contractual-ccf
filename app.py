import streamlit as st
from database import conectar_db

st.title("PRUEBA DE CONEXIÓN POSTGRESQL")

try:
    with conectar_db() as conn:
        st.success("Conexión exitosa a PostgreSQL")
except Exception as e:
    st.error(e)
