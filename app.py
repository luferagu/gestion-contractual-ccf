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
# CONEXIÓN A GOOGLE SHEETS
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
    sheet = client.open("BASE_PROCESOS_CCF").sheet1
    return sheet

# ==========================================================
# GENERAR CONSECUTIVO AUTOMÁTICO DESDE GOOGLE SHEETS
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

ID = generar_id()
st.info(f"ID_PROCESO generado automáticamente: {ID}")

# ==========================================================
# FUNCIÓN REEMPLAZO WORD
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
    ruta = os.path.join(PLANTILLAS, nombre)
    doc = Document(ruta)
    reemplazar(doc, datos)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================================
# ETAPA 1 — ESTUDIO PREVIO
# ==========================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

centro_costos = st.text_input("CENTRO DE COSTOS (10 números)")
programa = st.text_input("PROGRAMA (10 números)")
rubro = st.text_input("RUBRO (10 números)")
codigo_planeacion = st.text_input("CÓDIGO PLANEACIÓN")

caracteristicas = st.text_area("CARACTERÍSTICAS TÉCNICAS DEL BIEN")

oportunidad = st.multiselect("OPORTUNIDAD", [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
])

forma_pago = st.text_input("FORMA DE PAGO")

modalidad = st.selectbox("MODALIDAD", [
    "Contratación Directa",
    "Invitación Privada",
    "Convocatoria Abierta"
])

articulo = st.selectbox("ARTÍCULO", ["16","17","18"])
numeral = st.selectbox("NUMERAL", ["1","2","3","4"])
literal = st.selectbox("LITERAL", list("abcdefgh"))

valor = st.number_input("VALOR", min_value=0, step=1000)
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)

analisis_mercado = st.text_area("ANÁLISIS DE LAS CONDICIONES Y PRECIOS DEL MERCADO")

garantias = st.multiselect("GARANTÍAS CONTRACTUALES", [
    "Anticipo",
    "Cumplimiento",
    "Salarios y Prestaciones",
    "Responsabilidad Civil Extracontractual",
    "Estabilidad de la Obra",
    "Calidad del Servicio"
])

fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# ==========================================================
# BOTÓN GUARDAR EN GOOGLE SHEETS
# ==========================================================
if st.button("ENVIAR ETAPA 1 (GUARDAR EN BASE)"):

    sheet = conectar_sheet()

    fila = [
        ID,
        objeto,
        necesidad,
        justificacion,
        centro_costos,
        programa,
        rubro,
        codigo_planeacion,
        caracteristicas,
        ", ".join(oportunidad),
        forma_pago,
        modalidad,
        articulo,
        numeral,
        literal,
        valor,
        valor_letras,
        plazo,
        analisis_mercado,
        ", ".join(garantias),
        str(fecha_estudio)
    ]

    sheet.append_row(fila)

    st.success("Registro guardado correctamente en BASE_PROCESOS_CCF")

# ==========================================================
# GENERAR ESTUDIO PREVIO
# ==========================================================
if st.button("GENERAR ESTUDIO PREVIO"):

    datos = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "VALOR": f"${valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras
    }

    archivo = generar_descarga("estudio_previo.docx", datos)

    st.download_button(
        "DESCARGAR ESTUDIO PREVIO",
        data=archivo,
        file_name=f"estudio_previo_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.success("Sistema funcionando correctamente.")
