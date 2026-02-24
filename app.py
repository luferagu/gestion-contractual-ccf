import streamlit as st
import os
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
from database import conectar_db
import psycopg

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL")

# =====================================================
# GENERAR CONSECUTIVO DESDE POSTGRESQL
# =====================================================
def generar_id():
    conn = conectar_db()
    cursor = conn.cursor()

    year = date.today().year

    cursor.execute(
        "SELECT COUNT(*) FROM procesos WHERE id_proceso LIKE %s",
        (f"%-{year}",)
    )

    total = cursor.fetchone()[0]
    conn.close()

    return f"{total+1:03d}-{year}"

ID = generar_id()
st.info(f"ID_PROCESO: {ID}")

# =====================================================
# FUNCIONES AUXILIARES
# =====================================================
def valor_en_letras(valor):
    if valor == 0:
        return ""
    texto = num2words(valor, lang="es")
    texto = texto.replace("uno", "un")
    return texto.upper() + " PESOS M/CTE"

def limpiar_valor(texto):
    texto = texto.replace("$", "").replace(",", "").strip()
    return int(texto) if texto.isdigit() else 0

# =====================================================
# ETAPA 1 — ESTUDIO PREVIO
# =====================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

valor_input = st.text_input("VALOR ($)")
valor = limpiar_valor(valor_input)

if valor > 0:
    st.markdown(f"**{valor_en_letras(valor)}**")

plazo = st.number_input("PLAZO (días)", min_value=1)
fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# ---------- GUARDAR PROCESO ----------
if st.button("GUARDAR ETAPA 1"):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO procesos
            (id_proceso, objeto, necesidad, justificacion, valor, plazo, fecha_estudio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            ID,
            objeto,
            necesidad,
            justificacion,
            valor,
            plazo,
            fecha_estudio
        ))

        conn.commit()
        conn.close()

        st.success("Proceso guardado correctamente en PostgreSQL.")

    except Exception as e:
        st.error(f"Error al guardar: {e}")

# =====================================================
# ETAPA 3 — CONTRATOS
# =====================================================
st.header("ETAPA 3 — CONTRATOS")

tipo = st.selectbox("TIPO CONTRATO",
    ["Obra", "Consultoría", "Prestación de Servicios", "Suministro"])

supervisor = st.text_input("SUPERVISOR")
cdp = st.text_input("CDP")
fecha_firma = st.date_input("FECHA FIRMA")

# ---------- GUARDAR CONTRATO ----------
if st.button("GUARDAR CONTRATO"):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO contratos
            (id_proceso, tipo_contrato, supervisor, cdp, fecha_firma)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ID,
            tipo,
            supervisor,
            cdp,
            fecha_firma
        ))

        conn.commit()
        conn.close()

        st.success("Contrato guardado correctamente en PostgreSQL.")

    except Exception as e:
        st.error(f"Error al guardar contrato: {e}")

st.divider()
st.success("Sistema operativo en PostgreSQL (Supabase).")


