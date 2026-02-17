import streamlit as st
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
import os

st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL - CCF")

PLANTILLAS = "plantillas"

# ==========================================================
# GENERAR CONSECUTIVO AUTOMÁTICO
# ==========================================================
if "contador" not in st.session_state:
    st.session_state.contador = 1

year = date.today().year
ID = f"{st.session_state.contador:03d}-{year}"
st.info(f"ID_PROCESO generado automáticamente: {ID}")

# ==========================================================
# FUNCION REEMPLAZO EN WORD
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
imagenes = st.file_uploader("Adjuntar imágenes", accept_multiple_files=True)

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

plazo = st.number_input("PLAZO (Número)", min_value=1)

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
# GENERAR ESTUDIO PREVIO
# ==========================================================
if st.button("GENERAR ESTUDIO PREVIO"):

    datos = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "CENTRO_DE_COSTOS": centro_costos,
        "PROGRAMA": programa,
        "RUBRO": rubro,
        "CODIGO_PLANEACION": codigo_planeacion,
        "CARACTERISTICAS": caracteristicas,
        "OPORTUNIDAD": ", ".join(oportunidad),
        "FORMA_DE_PAGO": forma_pago,
        "MODALIDAD": modalidad,
        "ARTICULO": articulo,
        "NUMERAL": numeral,
        "LITERAL": literal,
        "VALOR": f"${valor:,.0f}".replace(",", "."),
        "VALOR_LETRAS": valor_letras,
        "PLAZO": plazo,
        "ANALISIS_MERCADO": analisis_mercado,
        "GARANTIAS": ", ".join(garantias),
        "FECHA_ESTUDIO": fecha_estudio
    }

    archivo = generar_descarga("estudio_previo.docx", datos)

    st.download_button(
        "DESCARGAR ESTUDIO PREVIO",
        data=archivo,
        file_name=f"estudio_previo_{ID}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ==========================================================
# ETAPA 2 — ÁREA DE COMPRAS
# ==========================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

proponente1 = st.text_input("PROPONENTE 1")
valor_prop1 = st.number_input("VALOR PROPUESTA 1", min_value=0)

proponente2 = st.text_input("PROPONENTE 2")
valor_prop2 = st.number_input("VALOR PROPUESTA 2", min_value=0)

identificacion_pn = st.text_input("IDENTIFICACIÓN PERSONA NATURAL")
identificacion_pj = st.text_input("IDENTIFICACIÓN PERSONA JURÍDICA")

if st.button("GENERAR SOLICITUD CDP"):
    archivo = generar_descarga("solicitud_cdp.docx", {"ID_PROCESO": ID})
    st.download_button("DESCARGAR CDP", archivo, f"solicitud_cdp_{ID}.docx")

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
# ETAPA 3 — ÁREA DE CONTRATOS
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

if st.button("GENERAR CONTRATO"):
    datos = {
        "ID_PROCESO": ID,
        "TIPO_CONTRATO": contrato_de,
        "SUPERVISOR": supervisor,
        "DISPONE": dispone,
        "CDP": cdp,
        "DURACION": f"{duracion_num} {duracion_tipo}",
        "EMPRESA": empresa,
        "FECHA_FIRMA": fecha_firma
    }

    archivo = generar_descarga("contrato.docx", datos)

    st.download_button(
        "DESCARGAR CONTRATO",
        archivo,
        f"contrato_{ID}.docx"
    )

st.success("Sistema funcionando correctamente.")
