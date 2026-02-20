import streamlit as st
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Gestión Contractual - CCF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("SISTEMA DE GESTIÓN CONTRACTUAL - CCF")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}
.main {
    background-color: #0f172a;
}
h1, h2, h3 {
    color: #f8fafc;
}
section[data-testid="stSidebar"] {
    background-color: #0b1220;
}
.stButton>button {
    background-color: #1e40af;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
}
.stButton>button:hover {
    background-color: #2563eb;
    color: white;
}
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
textarea {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 6px !important;
}
div[data-testid="stSelectbox"] > div {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 6px !important;
}
.block-container {
    padding-top: 2rem;
}
.banner-id {
    background: linear-gradient(90deg, #1e3a8a, #2563eb);
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-weight: bold;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

PLANTILLAS = "plantillas"

with st.sidebar:
    st.markdown("## 📑 MENÚ")
    st.markdown("---")

    menu = st.radio(
    "",
    [
        "📄 Estudio Previo",
        "🛒 Área de Compras",
        "📑 Área de Contratos"
    ]
)
)

    st.markdown("---")
    st.button("🔒 Cerrar sesión")


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

st.markdown("""
### 🔹 Flujo del Proceso
1️⃣ Estudio Previo &nbsp;&nbsp; ➝ &nbsp;&nbsp; 2️⃣ Compras &nbsp;&nbsp; ➝ &nbsp;&nbsp; 3️⃣ Contratación
""")

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
# ================= VISTAS DEL SISTEMA =================
# ==========================================================

if menu == "📄 Estudio Previo":

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

    oportunidad = st.multiselect(
        "OPORTUNIDAD",
        ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    )

    forma_pago = st.text_input("FORMA DE PAGO")

    col1, col2 = st.columns(2)
    with col1:
        modalidad = st.selectbox("MODALIDAD",
            ["Contratación Directa", "Invitación Privada", "Convocatoria Abierta"]
        )
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

    garantias = st.multiselect(
        "GARANTÍAS CONTRACTUALES",
        ["Anticipo", "Cumplimiento", "Salarios y Prestaciones",
         "Responsabilidad Civil Extracontractual",
         "Estabilidad de la Obra", "Calidad del Servicio"]
    )

    fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

    if st.button("ENVIAR ETAPA 1 (GUARDAR EN BASE)"):
        sheet = conectar_sheet()
        fila = [
            ID,objeto,necesidad,justificacion,centro,programa,
            rubro,codigo_planeacion,caracteristicas,
            ", ".join(oportunidad),forma_pago,modalidad,
            articulo,numeral,literal,valor,valor_letras,
            plazo,analisis,", ".join(garantias),
            str(fecha_estudio),"","","","","","","","","",""
        ]
        sheet.append_row(fila)
        st.success("ETAPA 1 guardada en Google Sheets")

elif menu == "🛒 Área de Compras":

    st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

    col1, col2 = st.columns(2)
    with col1:
        prop1 = st.text_input("PROPONENTE 1")
    with col2:
        val1 = st.number_input("VALOR PROPUESTA 1", min_value=0)

    col5, col6 = st.columns(2)
    with col5:
        prop2 = st.text_input("PROPONENTE 2")
    with col6:
        val2 = st.number_input("VALOR PROPUESTA 2", min_value=0)

elif menu == "📑 Área de Contratos":

    st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

    col1, col2, col3 = st.columns(3)
    with col1:
        contrato_de = st.selectbox(
            "TIPO DE CONTRATO",
            ["Obra","Consultoría","Prestación de Servicios",
             "Suministro","Compraventa","Arrendamiento","Seguros"]
        )
    with col2:
        supervisor = st.text_input("SUPERVISOR")
    with col3:
        cdp = st.text_input("CDP")

st.success("Sistema operativo correctamente.")
