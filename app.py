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


if "ID_PROCESO" not in st.session_state:
    st.session_state.ID_PROCESO = generar_id()

ID = st.session_state.ID_PROCESO
st.info(f"ID_PROCESO generado automáticamente: {ID}")


# ==========================================================
# FUNCIÓN REEMPLAZO ROBUSTA WORD
# ==========================================================
def reemplazar(doc, datos):

    for p in doc.paragraphs:
        full_text = "".join(run.text for run in p.runs)

        for k, v in datos.items():
            placeholder = f"{{{{{k}}}}}"
            if placeholder in full_text:
                full_text = full_text.replace(placeholder, str(v))

        for run in p.runs:
            run.text = ""

        if p.runs:
            p.runs[0].text = full_text

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    full_text = "".join(run.text for run in p.runs)

                    for k, v in datos.items():
                        placeholder = f"{{{{{k}}}}}"
                        if placeholder in full_text:
                            full_text = full_text.replace(placeholder, str(v))

                    for run in p.runs:
                        run.text = ""

                    if p.runs:
                        p.runs[0].text = full_text


# ==========================================================
# GENERAR DESCARGA WORD
# ==========================================================
def generar_descarga(nombre, datos):
    ruta = os.path.join(PLANTILLAS, nombre)
    doc = Document(ruta)
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

col1, col2 = st.columns(2)

with col1:
    centro = st.text_input("CENTRO DE COSTOS (10 números)")

with col2:
    programa = st.text_input("PROGRAMA (10 números)")

col3, col4 = st.columns(2)

with col3:
    rubro = st.text_input("RUBRO (10 números)")

with col4:
    codigo_planeacion = st.text_input("CÓDIGO PLANEACIÓN")

caracteristicas = st.text_area("CARACTERÍSTICAS TÉCNICAS DEL BIEN")

oportunidad = st.multiselect("OPORTUNIDAD", [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
])

forma_pago = st.text_input("FORMA DE PAGO")

col1, col2 = st.columns(2)

with col1:
    modalidad = st.selectbox("MODALIDAD", [
        "Contratación Directa",
        "Invitación Privada",
        "Convocatoria Abierta"
    ])

with col2:
    articulo = st.selectbox("ARTÍCULO", ["16","17","18"])


col3, col4 = st.columns(2)

with col3:
    numeral = st.selectbox("NUMERAL", ["1","2","3","4"])

with col4:
    literal = st.selectbox("LITERAL", list("abcdefgh"))


col5, col6 = st.columns(2)

with col5:
    valor = st.number_input("VALOR", min_value=0, step=1000)

with col6:
    plazo = st.number_input("PLAZO", min_value=1)

valor_letras = num2words(valor, lang="es").upper() if valor else ""

st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)


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

area_solicitante = st.selectbox(
    "ÁREA SOLICITANTE",
    [
        "Dirección Administrativa y Financiera",
        "Dirección de Desarrollo Empresarial",
        "Dirección de Desarrollo Institucional",
        "Dirección de Registros Públicos",
        "Dirección de Asuntos Jurídicos",
        "Dirección de control interno",
        "Área de Talento Humano"
    ]
)

if st.button("ENVIAR ETAPA 1 (GUARDAR EN BASE)"):

    sheet = conectar_sheet()

    fila = [
        ID,objeto,necesidad,justificacion,centro,programa,
        rubro,codigo_planeacion,caracteristicas,
        ", ".join(oportunidad),forma_pago,modalidad,
        articulo,numeral,literal,valor,valor_letras,
        plazo,analisis,", ".join(garantias),
        str(fecha_estudio),
        "", "", "", "", "", "", "", "", "", ""
    ]

    sheet.append_row(fila)
    st.success("ETAPA 1 guardada en Google Sheets")


if st.button("GENERAR ESTUDIO PREVIO"):

    datos = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "CENTRO_COSTOS": centro,
        "PROGRAMA": programa,
        "RUBRO": rubro,
        "CODIGO_PLANEACION": codigo_planeacion,
        "CARACTERISTICAS_TECNICAS": caracteristicas,
        "OPORTUNIDAD": ", ".join(oportunidad),
        "FORMA_PAGO": forma_pago,
        "MODALIDAD": modalidad,
        "ARTICULO": articulo,
        "NUMERAL": numeral,
        "LITERAL": literal,
        "VALOR": f"{valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras,
        "PLAZO": plazo,
        "ANALISIS": analisis,
        "GARANTIAS": ", ".join(garantias),
        "FECHA_ESTUDIO": fecha_estudio
    }

    archivo = generar_descarga("estudio_previo.docx", datos)

    st.download_button(
        "DESCARGAR ESTUDIO PREVIO",
        archivo,
        f"estudio_previo_{ID}.docx"
    )


# ==========================================================
# ================= ETAPA 2 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

col1, col2 = st.columns(2)

with col1:
    prop1 = st.text_input("PROPONENTE 1")

with col2:
    val1 = st.number_input("VALOR PROPUESTA 1", min_value=0)


col3, col4 = st.columns(2)

with col3:
    prop2 = st.text_input("PROPONENTE 2")

with col4:
    val2 = st.number_input("VALOR PROPUESTA 2", min_value=0)


col5, col6 = st.columns(2)

with col5:
    identificacion_pn = st.text_input("IDENTIFICACIÓN PERSONA NATURAL")

with col6:
    identificacion_pj = st.text_input("IDENTIFICACIÓN PERSONA JURÍDICA")



if st.button("ENVIAR ETAPA 2 (GUARDAR EN BASE)"):

    sheet = conectar_sheet()
    fila_num = buscar_fila(sheet, ID)

    if fila_num:
        sheet.update(
            f"V{fila_num}:AA{fila_num}",
            [[prop1, val1, prop2, val2, identificacion_pn, identificacion_pj]]
        )
        st.success("ETAPA 2 actualizada correctamente")
    else:
        st.error("Primero debe guardar ETAPA 1")


if st.button("GENERAR SOLICITUD CDP"):

    datos_cdp = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "CENTRO_COSTOS": centro,
        "PROGRAMA": programa,
        "RUBRO": rubro,
        "CODIGO_PLANEACION": codigo_planeacion,
        "VALOR": f"{valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras
    }

    archivo = generar_descarga("solicitud_cdp.docx", datos_cdp)

    st.download_button(
        "DESCARGAR CDP",
        archivo,
        f"solicitud_cdp_{ID}.docx"
    )


if st.button("GENERAR INVITACIÓN A COTIZAR"):
    archivo = generar_descarga("invitacion_cotizar.docx", {"ID_PROCESO": ID})
    st.download_button("DESCARGAR INVITACIÓN", archivo, f"invitacion_{ID}.docx")

if st.button("GENERAR INVITACIÓN PROPUESTA 1"):
    archivo = generar_descarga("invitacion_1_presentar_propuesta.docx", {"ID_PROCESO": ID})
    st.download_button("DESCARGAR PROPUESTA 1", archivo, f"inv_prop1_{ID}.docx")

if st.button("GENERAR INVITACIÓN PROPUESTA 2"):
    archivo = generar_descarga("invitacion_2_presentar_propuesta.docx", {"ID_PROCESO": ID})
    st.download_button("DESCARGAR PROPUESTA 2", archivo, f"inv_prop2_{ID}.docx")


# ==========================================================
# ================= ETAPA 3 =================
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

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
        sheet.update(
            f"AB{fila_num}:AH{fila_num}",
            [[contrato_de, supervisor, dispone, cdp,
              f"{duracion_num} {duracion_tipo}",
              empresa, str(fecha_firma)]]
        )
        st.success("ETAPA 3 actualizada correctamente")
    else:
        st.error("Primero debe guardar ETAPA 1")


if st.button("GENERAR CONTRATO"):
    archivo = generar_descarga("contrato.docx", {
        "ID_PROCESO": ID,
        "TIPO_CONTRATO": contrato_de,
        "SUPERVISOR": supervisor,
        "DISPONE": dispone,
        "CDP": cdp,
        "DURACION": f"{duracion_num} {duracion_tipo}",
        "EMPRESA": empresa,
        "FECHA_FIRMA": fecha_firma
    })

    st.download_button(
        "DESCARGAR CONTRATO",
        archivo,
        f"contrato_{ID}.docx"
    )


st.success("Sistema operativo correctamente.")






