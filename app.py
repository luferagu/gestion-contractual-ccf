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
# VARIABLES DE CONTROL DE ETAPA
# ==========================================================
if "etapa1_guardada" not in st.session_state:
    st.session_state.etapa1_guardada = False

if "etapa2_guardada" not in st.session_state:
    st.session_state.etapa2_guardada = False

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
    sheet = client.open("BASE_PROCESOS_CCF").sheet1
    return sheet

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

ID = generar_id()
st.info(f"ID_PROCESO generado automáticamente: {ID}")

# ==========================================================
# FUNCIONES WORD
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
# ================= ETAPA 1 =================
# ==========================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

centro = st.text_input("CENTRO DE COSTOS")
programa = st.text_input("PROGRAMA")
rubro = st.text_input("RUBRO")
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

analisis = st.text_area("ANÁLISIS DE LAS CONDICIONES Y PRECIOS DEL MERCADO")

garantias = st.multiselect("GARANTÍAS CONTRACTUALES", [
"Anticipo",
"Cumplimiento",
"Salarios y Prestaciones",
"Responsabilidad Civil Extracontractual",
"Estabilidad de la Obra",
"Calidad del Servicio"
])

fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

if st.button("ENVIAR ETAPA 1 (GUARDAR EN BASE)"):

    sheet = conectar_sheet()

    fila = [
        ID,objeto,necesidad,justificacion,centro,programa,
        rubro,codigo_planeacion,caracteristicas,
        ", ".join(oportunidad),forma_pago,modalidad,
        articulo,numeral,literal,
        valor,valor_letras,plazo,
        analisis,", ".join(garantias),
        str(fecha_estudio),
        "", "", "", "", "", "", "", "", "", "", "", ""
    ]

    sheet.append_row(fila)

    st.session_state.etapa1_guardada = True
    st.success("ETAPA 1 guardada correctamente")

# ==========================================================
# ================= ETAPA 2 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

if not st.session_state.etapa1_guardada:
    st.warning("Debe guardar ETAPA 1 antes de continuar.")
else:

    prop1 = st.text_input("PROPONENTE 1")
    val1 = st.number_input("VALOR PROPUESTA 1", min_value=0)

    prop2 = st.text_input("PROPONENTE 2")
    val2 = st.number_input("VALOR PROPUESTA 2", min_value=0)

    identificacion_pn = st.text_input("IDENTIFICACIÓN PERSONA NATURAL")
    identificacion_pj = st.text_input("IDENTIFICACIÓN PERSONA JURÍDICA")

    if st.button("ENVIAR ETAPA 2 (GUARDAR EN BASE)"):
        sheet = conectar_sheet()
        fila_num = buscar_fila(sheet, ID)

        if fila_num:
            sheet.update(f"V{fila_num}", prop1)
            sheet.update(f"W{fila_num}", val1)
            sheet.update(f"X{fila_num}", prop2)
            sheet.update(f"Y{fila_num}", val2)
            sheet.update(f"Z{fila_num}", identificacion_pn)
            sheet.update(f"AA{fila_num}", identificacion_pj)

            st.session_state.etapa2_guardada = True
            st.success("ETAPA 2 actualizada correctamente")

# ==========================================================
# ================= ETAPA 3 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

if not st.session_state.etapa2_guardada:
    st.warning("Debe guardar ETAPA 2 antes de continuar.")
else:

    contrato_de = st.selectbox("TIPO DE CONTRATO", [
    "Obra","Consultoría","Prestación de Servicios",
    "Suministro","Compraventa","Arrendamiento","Seguros"
    ])

    supervisor = st.text_input("SUPERVISOR")
    dispone = st.text_input("DISPONE")
    cdp = st.text_input("CDP")

    duracion_num = st.number_input("DURACIÓN", min_value=1)
    duracion_tipo = st.selectbox("TIPO DURACIÓN", ["Meses","Días"])

    empresa = st.selectbox("EMPRESA", ["Micro","Mini","Macro"])
    fecha_firma = st.date_input("FECHA FIRMA CONTRATO")

    if st.button("ENVIAR ETAPA 3 (GUARDAR EN BASE)"):
        sheet = conectar_sheet()
        fila_num = buscar_fila(sheet, ID)

        if fila_num:
            sheet.update(f"AB{fila_num}", contrato_de)
            sheet.update(f"AC{fila_num}", supervisor)
            sheet.update(f"AD{fila_num}", dispone)
            sheet.update(f"AE{fila_num}", cdp)
            sheet.update(f"AF{fila_num}", f"{duracion_num} {duracion_tipo}")
            sheet.update(f"AG{fila_num}", empresa)
            sheet.update(f"AH{fila_num}", str(fecha_firma))

            st.success("ETAPA 3 actualizada correctamente")

st.success("Sistema operativo correctamente.")
