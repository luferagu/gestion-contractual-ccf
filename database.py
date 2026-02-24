import psycopg2
import streamlit as st

def conectar_db():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def crear_tablas():
    pass
pass

