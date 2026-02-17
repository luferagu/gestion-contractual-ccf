import streamlit as st
import pandas as pd
from datetime import date
from num2words import num2words
from docx import Document
import gspread
from google.oauth2.service_account import Credentials
import os

st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL - CCF")

PLANTILLAS = "plantillas"
SALIDA = "salida"

os.makedirs(SALIDA, exist_ok=True)

# ---------------------------------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------------------------------

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

# ---------------------------------------------------
# GENERAR CONSECUTIVO AUTOMÁTICO
# ---------------------------------------------------

def generar_id():
    sheet = conectar_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    year = date.today().year

    if df.empty:
        consecutivo = 1
    else:
        df_year = df[df["ID_PROCESO"].astype(str).str.contains(str(year), na=False)]
        consecutivo = len(df_year) + 1

    return f"{consecutivo:03d}-{year}"

ID = generar_id()
st.info(f"ID_PROCESO generado automáticamente: {ID}")

# ---------------------------------------------------
# FUNCIONES WORD
# ---------------------------------------------------

def reemplazar(doc, datos):
    for p in doc.paragraphs:
        for k, v in datos.items():
            if f"{{{{{k}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{k}}}}}", str(v))

def generar_doc(nombre, datos):
    doc = Document(os.path.join(PLANTILLAS, nombre))
    reemplazar(doc, datos)
    ruta = os.path.join(SALIDA, f"{nombre[:-5]}_{ID}.docx")
    doc.save(ruta)
    return ruta

# ---------------------------------------------------
# ETAPA 1
# ---------------------------------------------------

st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACION")

centro = st.text_input("CENTRO_DE_COSTOS (10 dígitos)")
programa = st.text_input("PROGRAMA (10 dígitos)")
rubro = st.text_input("RUBRO (10 dígitos)")
codigo = st.text_input("CODIGO_PLANEACION")

caracteristicas = st.text_area("CARACTERISTICAS_TECNICAS")
oportunidad = st.multiselect("OPORTUNIDAD", [
"Enero","Febrero","Marzo","Abril","Mayo","Junio",
"Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])

forma_pago = st.text_input("FORMA_DE_PAGO")

modalidad = st.selectbox("MODALIDAD",
["Contratación Directa","Invitación Privada","Convocatoria Abierta"])

articulo = st.selectbox("ARTICULO",["16","17","18"])
numeral = st.selectbox("NUMERAL",["1","2","3","4"])
literal = st.selectbox("LITERAL",list("abcdefgh"))

valor = st.number_input("VALOR", min_value=0, step=1000, format="%d")
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR_LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)

analisis = st.text_area("ANALISIS_MERCADO")
fecha_estudio = st.date_input("FECHA_ESTUDIO", value=date.today())

if st.button("ENVIAR ETAPA 1"):
    sheet = conectar_sheet()

    sheet.append_row([
        ID,
        objeto,
        necesidad,
        justificacion,
        centro,
        programa,
        rubro,
        codigo,
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
        analisis,
        fecha_estudio.strftime("%Y-%m-%d"),
        "", "", "", "",
        "", "", "", ""
    ])

    st.success("ETAPA 1 guardada en Google Sheets")

if st.button("GENERAR ESTUDIO PREVIO"):
    generar_doc("estudio_previo.docx", {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "VALOR": valor,
        "VALOR_LETRAS": valor_letras
    })
    st.success("Documento generado en carpeta salida")

# ---------------------------------------------------
# ETAPA 2
# ---------------------------------------------------

st.header("ESPACIO RESERVADO PARA EL AREA DE COMPRAS")

prop1 = st.text_input("PROPONENTE_1")
val1 = st.number_input("VALOR_PROP_1", min_value=0)

prop2 = st.text_input("PROPONENTE_2")
val2 = st.number_input("VALOR_PROP_2", min_value=0)

if st.button("GENERAR SOLICITUD CDP"):
    generar_doc("solicitud_cdp.docx", {"ID_PROCESO": ID})

if st.button("GENERAR INVITACION COTIZAR"):
    generar_doc("invitacion_cotizar.docx", {"ID_PROCESO": ID})

# ---------------------------------------------------
# ETAPA 3
# ---------------------------------------------------

st.header("ESPACIO RESERVADO PARA EL AREA DE CONTRATOS")

contrato_de = st.selectbox("TIPO_CONTRATO",
["Obra","Consultoría","Prestación de Servicios","Suministro",
"Compraventa","Arrendamiento","Seguros"])

supervisor = st.text_input("SUPERVISOR")
cdp = st.text_input("CDP")
fecha_firma = st.date_input("FECHA_FIRMA", value=date.today())

if st.button("GENERAR CONTRATO"):
    generar_doc("contrato.docx", {
        "ID_PROCESO": ID,
        "SUPERVISOR": supervisor,
        "FECHA_FIRMA": fecha_firma
    })
    st.success("Contrato generado correctamente")
