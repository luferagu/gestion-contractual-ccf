import streamlit as st
import pandas as pd
import os
from datetime import date
from num2words import num2words
from docx import Document

st.set_page_config(layout="wide")
st.title("SISTEMA DE GESTIÓN CONTRACTUAL")

BASE = "1_BASE_DATOS/procesos.xlsx"
PLANTILLAS = "2_PLANTILLAS"
SALIDA = "3_SALIDA"

os.makedirs("1_BASE_DATOS", exist_ok=True)
os.makedirs("3_SALIDA", exist_ok=True)

# -------------------------------------------------
# CREAR BASE DE DATOS COMPLETA (SOLO LA PRIMERA VEZ)
# -------------------------------------------------
if not os.path.exists(BASE):
    df = pd.DataFrame(columns=[
        "ID_PROCESO","OBJETO","NECESIDAD","JUSTIFICACION",
        "CENTRO_COSTOS","PROGRAMA","RUBRO","CODIGO_PLANEACION",
        "CARACTERISTICAS","OPORTUNIDAD","FORMA_PAGO",
        "MODALIDAD","ARTICULO","NUMERAL","LITERAL",
        "VALOR","VALOR_LETRAS","PLAZO","ANALISIS_MERCADO",
        "FECHA_ESTUDIO",
        "PROPONENTE_1","VALOR_PROP_1","PROPONENTE_2","VALOR_PROP_2",
        "TIPO_CONTRATO","SUPERVISOR","CDP","FECHA_FIRMA"
    ])
    df.to_excel(BASE, index=False)

# -------------------------------------------------
# GENERAR CONSECUTIVO AUTOMÁTICO
# -------------------------------------------------
def generar_id():
    year = date.today().year
    df = pd.read_excel(BASE)
    df_year = df[df["ID_PROCESO"].astype(str).str.contains(str(year), na=False)]
    consecutivo = len(df_year) + 1
    return f"{consecutivo:03d}-{year}"

ID = generar_id()
st.info(f"ID_PROCESO generado automáticamente: {ID}")

# -------------------------------------------------
# FUNCIÓN ROBUSTA DE REEMPLAZO WORD
# -------------------------------------------------
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
    doc = Document(os.path.join(PLANTILLAS, nombre))
    reemplazar_doc(doc, datos)
    salida = os.path.join(SALIDA, f"{nombre[:-5]}_{ID}.docx")
    doc.save(salida)
    return salida

# =================================================
# ETAPA 1 — ESTUDIO PREVIO
# =================================================
st.header("ETAPA 1 — ESTUDIO PREVIO")

objeto = st.text_area("OBJETO")
necesidad = st.text_area("NECESIDAD")
justificacion = st.text_area("JUSTIFICACIÓN")

centro = st.text_input("CENTRO DE COSTOS")
programa = st.text_input("PROGRAMA")
rubro = st.text_input("RUBRO")
codigo = st.text_input("CÓDIGO PLANEACIÓN")

caracteristicas = st.text_area("CARACTERÍSTICAS TÉCNICAS")

oportunidad = st.multiselect("OPORTUNIDAD",
["Enero","Febrero","Marzo","Abril","Mayo","Junio",
"Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])

forma_pago = st.text_input("FORMA DE PAGO")

modalidad = st.selectbox("MODALIDAD",
["Contratación Directa","Invitación Privada","Convocatoria Abierta"])

articulo = st.selectbox("ARTÍCULO",["16","17","18"])
numeral = st.selectbox("NUMERAL",["1","2","3","4"])
literal = st.selectbox("LITERAL",list("abcdefgh"))

valor = st.number_input("VALOR", min_value=0, step=1000)
valor_letras = num2words(valor, lang="es").upper() if valor else ""
st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

plazo = st.number_input("PLAZO", min_value=1)

analisis = st.text_area("ANÁLISIS DEL MERCADO")

fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

# -------- GUARDAR ETAPA 1 --------
if st.button("GUARDAR ETAPA 1"):
    df = pd.read_excel(BASE)

    nuevo = {
        "ID_PROCESO": ID,
        "OBJETO": objeto,
        "NECESIDAD": necesidad,
        "JUSTIFICACION": justificacion,
        "CENTRO_COSTOS": centro,
        "PROGRAMA": programa,
        "RUBRO": rubro,
        "CODIGO_PLANEACION": codigo,
        "CARACTERISTICAS": caracteristicas,
        "OPORTUNIDAD": ", ".join(oportunidad),
        "FORMA_PAGO": forma_pago,
        "MODALIDAD": modalidad,
        "ARTICULO": articulo,
        "NUMERAL": numeral,
        "LITERAL": literal,
        "VALOR": valor,
        "VALOR_LETRAS": valor_letras,
        "PLAZO": plazo,
        "ANALISIS_MERCADO": analisis,
        "FECHA_ESTUDIO": fecha_estudio
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_excel(BASE, index=False)
    st.success("ETAPA 1 almacenada en base de datos")

# -------- GENERAR ESTUDIO --------
if st.button("GENERAR ESTUDIO PREVIO"):
    generar_doc("estudio_previo.docx", nuevo)
    st.success("Documento generado en 3_SALIDA")

# =================================================
# ETAPA 2 — COMPRAS
# =================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE COMPRAS")

prop1 = st.text_input("PROPONENTE 1")
val1 = st.number_input("VALOR PROPUESTA 1", min_value=0)

prop2 = st.text_input("PROPONENTE 2")
val2 = st.number_input("VALOR PROPUESTA 2", min_value=0)

if st.button("ACTUALIZAR ETAPA 2"):
    df = pd.read_excel(BASE)
    df.loc[df["ID_PROCESO"] == ID, ["PROPONENTE_1","VALOR_PROP_1","PROPONENTE_2","VALOR_PROP_2"]] = [prop1,val1,prop2,val2]
    df.to_excel(BASE, index=False)
    st.success("ETAPA 2 actualizada")

# =================================================
# ETAPA 3 — CONTRATOS
# =================================================
st.header("ESPACIO RESERVADO PARA EL ÁREA DE CONTRATOS")

tipo = st.selectbox("TIPO CONTRATO",
["Obra","Consultoría","Prestación de Servicios","Suministro"])

supervisor = st.text_input("SUPERVISOR")
cdp = st.text_input("CDP")
fecha_firma = st.date_input("FECHA FIRMA")

if st.button("ACTUALIZAR ETAPA 3"):
    df = pd.read_excel(BASE)
    df.loc[df["ID_PROCESO"] == ID, ["TIPO_CONTRATO","SUPERVISOR","CDP","FECHA_FIRMA"]] = [tipo,supervisor,cdp,fecha_firma]
    df.to_excel(BASE, index=False)
    st.success("ETAPA 3 actualizada")

if st.button("GENERAR CONTRATO"):
    generar_doc("contrato.docx", {
        "ID_PROCESO": ID,
        "SUPERVISOR": supervisor,
        "FECHA": fecha_firma
    })
    st.success("Contrato generado")

st.success("Sistema funcionando correctamente.")
