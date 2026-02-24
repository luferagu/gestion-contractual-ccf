import psycopg2
import streamlit as st

def conectar_db():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require"
    )
