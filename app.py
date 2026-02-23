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

valor_input = st.text_input("VALOR")

valor = limpiar_valor(valor_input)
if valor > 0:
    st.markdown(f"**{valor_en_letras(valor)}**")

plazo = st.number_input("PLAZO", min_value=1)
fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

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

if st.button("GENERAR ESTUDIO PREVIO"):
    archivo = generar_doc("estudio_previo.docx", {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "VALOR": f"$ {valor:,.0f}",
        "VALOR_LETRAS": valor_en_letras(valor),
        "PLAZO": plazo
    })

    st.download_button(
        "Descargar Estudio Previo",
        archivo,
        file_name=f"estudio_previo_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# =====================================================
# ETAPA 2 — ÁREA DE COMPRAS
# =====================================================
st.header("ETAPA 2 — ÁREA DE COMPRAS")

# ---------------- PROPONENTE 1 ----------------
st.subheader("DATOS PROPONENTE 1")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    proponente_1 = st.text_input("PROPONENTE 1")

with col2:
    tipo_persona_1 = st.selectbox("TIPO PERSONA",
        ["Persona Natural", "Persona Jurídica"], key="tipo1")

with col3:
    identificacion_1 = st.text_input(
        "CC" if tipo_persona_1 == "Persona Natural" else "NIT",
        key="id1"
    )

with col4:
    valor_input_1 = st.text_input("VALOR PROPUESTA", key="valor1")

valor_prop_1 = limpiar_valor(valor_input_1)

with col5:
    if valor_prop_1 > 0:
        st.markdown(f"**{valor_en_letras(valor_prop_1)}**")

# ---------------- PROPONENTE 2 ----------------
st.subheader("DATOS PROPONENTE 2")

col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    proponente_2 = st.text_input("PROPONENTE 2")

with col7:
    tipo_persona_2 = st.selectbox("TIPO PERSONA",
        ["Persona Natural", "Persona Jurídica"], key="tipo2")

with col8:
    identificacion_2 = st.text_input(
        "CC" if tipo_persona_2 == "Persona Natural" else "NIT",
        key="id2"
    )

with col9:
    valor_input_2 = st.text_input("VALOR PROPUESTA", key="valor2")

valor_prop_2 = limpiar_valor(valor_input_2)

with col10:
    if valor_prop_2 > 0:
        st.markdown(f"**{valor_en_letras(valor_prop_2)}**")

# ---------------- DOCUMENTOS COMPRAS ----------------
st.subheader("GENERACIÓN DOCUMENTOS ÁREA DE COMPRAS")

documentos_compras = [
    "solicitud_cdp.docx",
    "invitacion_cotizar.docx",
    "invitacion_1_presentar_propuesta.docx",
    "invitacion_2_presentar_propuesta.docx",
    "Verificacion_de_requisitos.docx"
]

for doc_name in documentos_compras:
    if st.button(f"GENERAR {doc_name.replace('.docx','').upper()}"):
        archivo = generar_doc(doc_name, {"ID_PROCESO": ID})
        st.download_button(
            f"Descargar {doc_name}",
            archivo,
            file_name=f"{doc_name.replace('.docx','')}_{ID}.docx"
        )

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
        "VALOR": f"$ {valor:,.0f}"
    })

    st.download_button(
        "Descargar Contrato",
        archivo,
        file_name=f"contrato_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.success("Sistema funcionando correctamente.")
