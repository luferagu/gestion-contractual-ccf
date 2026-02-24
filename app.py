import streamlit as st
from database import conectar_db

st.title("PRUEBA DE CONEXIÓN POSTGRESQL")

try:
    conn = conectar_db()
    st.success("Conexión exitosa a PostgreSQL")
    conn.close()
except Exception as e:
    st.error(e)
