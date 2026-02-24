import psycopg2
import streamlit as st
from urllib.parse import urlparse

def conectar_db():
    url = urlparse(st.secrets["DATABASE_URL"])

    conn = psycopg2.connect(
        dbname=url.path[1:],  # quita el '/'
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        sslmode="require",
        options='-c client_encoding=UTF8'
    )

    return conn
