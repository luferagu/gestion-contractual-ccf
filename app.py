import streamlit as st
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL - CCF")

PLANTILLAS = "plantillas"

# ==========================================================
# VARIABLES DE CONTROL
# ==========================================================
if "id_actual" not in st.session_state:
    st.session_state.id_actual = None

if "etapa1" not in st.session_state:
    st.session_state.etapa1 = False

if "etapa2" not in st.session_state:
    st.session_state.etapa2 = False


# ==========================================================
# CONEXIÓN GOOGLE SHEETS
# ==========================================================
def conectar_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client.open("BASE_PROCESOS_CCF").sheet1


# ==========================================================
# GENERAR CONSECUTIVO ANUAL
# ==========================================================
def generar_id():
    sheet = conectar_sheet()
    registros = sheet.get_all_records()
    year = str(date.today().year)
    contador = 1

    for r in registros:
        if year in str(r.get("ID_PROCESO", "")):
            contador += 1

    return f"{contador:03d}-{year}"


# ==========================================================
# BUSCAR FILA POR ID
# ==========================================================
def buscar_fila(sheet, id_proceso):
    registros = sheet.get_all_records()
    for i, fila in enumerate(registros, start=2):
        if str(fila.get("ID_PROCESO")) == str(id_proceso):
            return i
    return None


# ==========================================================
# WORD
# ==========================================================
def reemplazar(doc, datos):
    for p in doc.paragraphs:
        for k, v in datos.items():
            if f"{{{{{k}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{k}}}}}", str(v))

    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for k, v in datos.items():
                    if f"{{{{{k}}}}}" in c.text:
                        c.text = c.text.replace(f"{{{{{k}}}}}", str(v))


def generar_descarga(nombre, datos):
    doc = Document(os.path.join(PLANTILLAS, nombre))
    reemplazar(doc, datos)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ==========================================================
# ID INICIAL
# ==========================================================
if st.session_state.id_actual is None:
    st.session_state.id_actual = generar_id()

ID = st.session_state.id_actual
st.info(f"ID_PROCESO: {ID}")

# ==========================================================
# ================= ETAPA 1 =================
# ==========================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

modalidad = st.selectbox("MODALIDAD", [
    "Contratación Directa",
    "Invitación Privada",
    "Convocatoria Abierta"
])

valor = st.number_input("VALOR", min_value=0, step=1000)
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)
fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# -------- GUARDAR ETAPA 1 --------
if st.button("ENVIAR ETAPA 1 (guardar en base)"):
    sheet = conectar_sheet()

    fila = [
        ID, objeto, necesidad, justificacion,
        "", "", "", "", "",
        "", "", modalidad,
        "", "", "",
        valor, valor_letras,
        plazo, "",
        "",
        str(fecha_estudio),
        "", "", "", "", "", "", "", "", "", "", "", ""
    ]

    sheet.append_row(fila)
    st.session_state.etapa1 = True
    st.success("ETAPA 1 guardada correctamente")


# -------- GENERAR WORD ETAPA 1 --------
if st.button("GENERAR ESTUDIO PREVIO"):
    archivo = generar_descarga("estudio_previo.docx", {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "VALOR": f"${valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras
    })

    st.download_button("DESCARGAR ESTUDIO PREVIO", archivo, f"estudio_previo_{ID}.docx")


# ==========================================================
# ================= ETAPA 2 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

if not st.session_state.etapa1:
    st.warning("Debe guardar ETAPA 1 antes de continuar.")
else:

    prop1 = st.text_input("PROPONENTE 1")
    val1 = st.number_input("VALOR PROPUESTA 1", min_value=0)

    prop2 = st.text_input("PROPONENTE 2")
    val2 = st.number_input("VALOR PROPUESTA 2", min_value=0)

    if st.button("ENVIAR ETAPA 2 (guardar en base)"):

        sheet = conectar_sheet()
        fila_num = buscar_fila(sheet, ID)

        if fila_num:
            sheet.update(f"V{fila_num}", prop1)
            sheet.update(f"W{fila_num}", val1)
            sheet.update(f"X{fila_num}", prop2)
            sheet.update(f"Y{fila_num}", val2)

            st.session_state.etapa2 = True
            st.success("ETAPA 2 guardada correctamente")

    # BOTONES WORD
    if st.button("GENERAR SOLICITUD CDP"):
        archivo = generar_descarga("solicitud_cdp.docx", {"ID_PROCESO": ID})
        st.download_button("DESCARGAR CDP", archivo, f"solicitud_cdp_{ID}.docx")

    if st.button("GENERAR INVITACIÓN A COTIZAR"):
        archivo = generar_descarga("invitacion_cotizar.docx", {"ID_PROCESO": ID})
        st.download_button("DESCARGAR INVITACIÓN", archivo, f"invitacion_{ID}.docx")


# ==========================================================
# ================= ETAPA 3 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

if not st.session_state.etapa2:
    st.warning("Debe guardar ETAPA 2 antes de continuar.")
else:

    contrato_de = st.selectbox("TIPO DE CONTRATO", [
        "Obra","Consultoría","Prestación de Servicios",
        "Suministro","Compraventa","Arrendamiento","Seguros"
    ])

    supervisor = st.text_input("SUPERVISOR")
    fecha_firma = st.date_input("FECHA FIRMA")

    if st.button("ENVIAR ETAPA 3 (guardar en base)"):
        sheet = conectar_sheet()
        fila_num = buscar_fila(sheet, ID)

        if fila_num:
            sheet.update(f"AB{fila_num}", contrato_de)
            sheet.update(f"AC{fila_num}", supervisor)
            sheet.update(f"AH{fila_num}", str(fecha_firma))

            st.success("ETAPA 3 guardada correctamente")

    if st.button("GENERAR CONTRATO"):
        archivo = generar_descarga("contrato.docx", {
            "ID_PROCESO": ID,
            "TIPO_CONTRATO": contrato_de,
            "SUPERVISOR": supervisor,
            "FECHA_FIRMA": fecha_firma
        })

        st.download_button("DESCARGAR CONTRATO", archivo, f"contrato_{ID}.docx")


st.success("Sistema operativo correctamente.")
