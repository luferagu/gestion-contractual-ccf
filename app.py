import streamlit as st
import os
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
from database import conectar_db, crear_tablas

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL")

crear_tablas()

PLANTILLAS = "2_PLANTILLAS"
os.makedirs(PLANTILLAS, exist_ok=True)

# =====================================================
# GENERAR CONSECUTIVO DESDE SQL
# =====================================================
def generar_id():
    conn = conectar_db()
    cursor = conn.cursor()

    year = date.today().year
    cursor.execute("SELECT COUNT(*) FROM procesos WHERE id_proceso LIKE ?", (f"%-{year}",))
    total = cursor.fetchone()[0]

    conn.close()
    return f"{total+1:03d}-{year}"

ID = generar_id()
st.info(f"ID_PROCESO: {ID}")

# =====================================================
# FUNCIONES WORD
# =====================================================
def reemplazar_texto(parrafo, datos):
    texto = "".join(run.text for run in parrafo.runs)
    for k, v in datos.items():
        texto = texto.replace(f"{{{{{k}}}}}", str(v))
    for run in parrafo.runs:
        run.text = ""
    if parrafo.runs:
        parrafo.runs[0].text = texto

def reemplazar_doc(doc, datos):
    for p in doc.paragraphs:
        reemplazar_texto(p, datos)
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    reemplazar_texto(p, datos)

def generar_doc(nombre, datos):
    ruta = os.path.join(PLANTILLAS, nombre)
    doc = Document(ruta)
    reemplazar_doc(doc, datos)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# =====================================================
# ETAPA 1 — ESTUDIO PREVIO
# =====================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

valor = st.number_input("VALOR", min_value=0, step=1000)
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)
fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# Guardar Proceso
if st.button("GUARDAR ETAPA 1"):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO procesos
        (id_proceso, objeto, necesidad, justificacion, valor, plazo, fecha_estudio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ID, objeto, necesidad, justificacion,
        valor, plazo, str(fecha_estudio)
    ))

    conn.commit()
    conn.close()

    st.success("Proceso guardado correctamente.")

# Generar Estudio Previo
if st.button("GENERAR ESTUDIO PREVIO"):
    archivo = generar_doc("estudio_previo.docx", {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "VALOR": valor,
        "VALOR_LETRAS": valor_letras,
        "PLAZO": plazo
    })

    st.download_button(
        "Descargar Estudio Previo",
        data=archivo,
        file_name=f"estudio_previo_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# =====================================================
# ETAPA 2 — ÁREA DE COMPRAS
# =====================================================
st.header("ETAPA 2 — ÁREA DE COMPRAS")

st.subheader("Generación de Documentos")

if st.button("GENERAR SOLICITUD CDP"):
    archivo = generar_doc("solicitud_cdp.docx", {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "VALOR": valor
    })
    st.download_button("Descargar Solicitud CDP", archivo,
                       file_name=f"solicitud_cdp_{ID}.docx")

if st.button("GENERAR INVITACIÓN A COTIZAR"):
    archivo = generar_doc("invitacion_cotizar.docx", {
        "ID_PROCESO": ID
    })
    st.download_button("Descargar Invitación Cotizar", archivo,
                       file_name=f"invitacion_cotizar_{ID}.docx")

if st.button("GENERAR INVITACIÓN PROPUESTA 1"):
    archivo = generar_doc("invitacion_1_presentar_propuesta.docx", {
        "ID_PROCESO": ID
    })
    st.download_button("Descargar Invitación Propuesta 1", archivo,
                       file_name=f"inv_prop1_{ID}.docx")

if st.button("GENERAR INVITACIÓN PROPUESTA 2"):
    archivo = generar_doc("invitacion_2_presentar_propuesta.docx", {
        "ID_PROCESO": ID
    })
    st.download_button("Descargar Invitación Propuesta 2", archivo,
                       file_name=f"inv_prop2_{ID}.docx")

if st.button("GENERAR VERIFICACIÓN DE REQUISITOS"):
    archivo = generar_doc("Verificacion_de_requisitos.docx", {
        "ID_PROCESO": ID
    })
    st.download_button("Descargar Verificación", archivo,
                       file_name=f"verificacion_{ID}.docx")

# =====================================================
# ETAPA 3 — CONTRATOS
# =====================================================
st.header("ETAPA 3 — CONTRATOS")

tipo = st.selectbox("TIPO CONTRATO",
    ["Obra","Consultoría","Prestación de Servicios","Suministro"])

supervisor = st.text_input("SUPERVISOR")
cdp = st.text_input("CDP")
fecha_firma = st.date_input("FECHA FIRMA")

if st.button("GUARDAR CONTRATO"):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contratos
        (id_proceso, tipo_contrato, supervisor, cdp, fecha_firma)
        VALUES (?, ?, ?, ?, ?)
    """, (
        ID, tipo, supervisor, cdp, str(fecha_firma)
    ))

    conn.commit()
    conn.close()

    st.success("Contrato guardado correctamente.")

if st.button("GENERAR CONTRATO"):
    archivo = generar_doc("contrato.docx", {
        "ID_PROCESO": ID,
        "SUPERVISOR": supervisor,
        "FECHA": fecha_firma,
        "VALOR": valor
    })

    st.download_button(
        "Descargar Contrato",
        data=archivo,
        file_name=f"contrato_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.success("Sistema funcionando correctamente.")
