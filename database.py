import psycopg
import streamlit as st

def conectar_db():
    return psycopg.connect(st.secrets["DATABASE_URL"])

