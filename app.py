import streamlit as st
import os
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO

st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL - CCF")

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
PLANTILLAS = "plantillas"

# -------------------------------------------------
# GENERAR CONSECUTIVO AUTOMÁTICO SIMPLE
# (puede luego conectarlo a Google Sheets)
# -------------------------------------------------
if "contador" not in st.session_state:
    st.session_state.contador = 1

year = date.today().year
ID = f"{st.session_state.contador:03d}-{year}"

st.info(f"ID_PROCESO generado automáticamente: {ID}")

# -------------------------------------------------
# FUNCIÓN REEMPLAZO DE VARIABLES EN WORD
# -------------------------------------------------
def reemplazar_variables(doc, datos):

    for p in doc.paragraphs:
        for key, value in datos.items():
            if f"{{{{{key}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{key}}}}}", str(value))

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in datos.items():
                    if f"{{{{{key}}}}}" in cell.text:
                        cell.text = cell.text.replace(f"{{{{{key}}}}}", str(value))

# -------------------------------------------------
# GENERAR DOCUMENTO Y DESCARGAR
# -------------------------------------------------
def generar_y_descargar(nombre_plantilla, datos):

    ruta = os.path.join(PLANTILLAS, nombre_plantilla)
    doc = Document(ruta)

    reemplazar_variables(doc, datos)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# -------------------------------------------------
# FORMULARIO PRINCIPAL
# -------------------------------------------------
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

valor = st.number_input("VALOR", min_value=0, step=1000)
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)

fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# -------------------------------------------------
# GENERAR ESTUDIO PREVIO
# -------------------------------------------------
if st.button("GENERAR ESTUDIO PREVIO"):

    datos = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "VALOR": f"${valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras,
        "PLAZO": plazo,
        "FECHA_ESTUDIO": fecha_estudio
    }

    archivo = generar_y_descargar("estudio_previo.docx", datos)

    st.download_button(
        label="DESCARGAR ESTUDIO PREVIO",
        data=archivo,
        file_name=f"estudio_previo_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# -------------------------------------------------
# ETAPA 2 — COMPRAS
# -------------------------------------------------
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

if st.button("GENERAR SOLICITUD CDP"):

    datos = {"ID_PROCESO": ID}

    archivo = generar_y_descargar("solicitud_cdp.docx", datos)

    st.download_button(
        label="DESCARGAR SOLICITUD CDP",
        data=archivo,
        file_name=f"solicitud_cdp_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if st.button("GENERAR INVITACIÓN A COTIZAR"):

    datos = {"ID_PROCESO": ID}

    archivo = generar_y_descargar("invitacion_cotizar.docx", datos)

    st.download_button(
        label="DESCARGAR INVITACIÓN",
        data=archivo,
        file_name=f"invitacion_cotizar_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# -------------------------------------------------
# ETAPA 3 — CONTRATOS
# -------------------------------------------------
st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

supervisor = st.text_input("SUPERVISOR")
fecha_firma = st.date_input("FECHA FIRMA")

if st.button("GENERAR CONTRATO"):

    datos = {
        "ID_PROCESO": ID,
        "SUPERVISOR": supervisor,
        "FECHA_FIRMA": fecha_firma
    }

    archivo = generar_y_descargar("contrato.docx", datos)

    st.download_button(
        label="DESCARGAR CONTRATO",
        data=archivo,
        file_name=f"contrato_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.success("Sistema operativo correctamente.")
