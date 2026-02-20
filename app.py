import streamlit as st
from datetime import date
from num2words import num2words
from docx import Document
from io import BytesIO
import os
import gspread
from google.oauth2.service_account import Credentials

# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
st.set_page_config(
    page_title="Sistema de Gestión Contractual - CCF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    return client.open("BASE_PROCESOS_CCF").sheet1


def buscar_fila(sheet, id_proceso):
    registros = sheet.get_all_records()
    for i, fila in enumerate(registros, start=2):
        if str(fila.get("ID_PROCESO")) == str(id_proceso):
            return i
    return None


def generar_id():
    sheet = conectar_sheet()
    registros = sheet.get_all_records()
    year = str(date.today().year)
    consecutivos = []

    for r in registros:
        idp = str(r.get("ID_PROCESO", ""))
        if idp.endswith(year):
            numero = idp.split("-")[0]
            consecutivos.append(int(numero))

    nuevo = max(consecutivos) + 1 if consecutivos else 1
    return f"{nuevo:03d}-{year}"


# ==========================================================
# CONTROL DE ESTADO
# ==========================================================
if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"

if "ID_PROCESO" not in st.session_state:
    st.session_state.ID_PROCESO = generar_id()

ID = st.session_state.ID_PROCESO


# ==========================================================
# SIDEBAR FUNCIONAL
# ==========================================================
with st.sidebar:

    st.markdown("## 📑 MENÚ")
    st.markdown("---")

    if st.button("➕ Nuevo Proceso", key="nuevo"):
        st.session_state.ID_PROCESO = generar_id()
        st.session_state.menu = "Procesos"
        st.rerun()

    if st.button("🏠 Inicio", key="inicio"):
        st.session_state.menu = "Inicio"

    if st.button("📂 Procesos", key="procesos"):
        st.session_state.menu = "Procesos"

    if st.button("📜 Contratos", key="contratos"):
        st.session_state.menu = "Contratos"

    if st.button("📊 Reportes", key="reportes"):
        st.session_state.menu = "Reportes"

    if st.button("⚙ Configuración", key="config"):
        st.session_state.menu = "Configuracion"

    st.markdown("---")

    if st.button("🔒 Cerrar sesión", key="logout"):
        st.session_state.clear()
        st.rerun()


# ==========================================================
# FUNCIONES WORD
# ==========================================================
def reemplazar(doc, datos):
    for p in doc.paragraphs:
        texto = "".join(run.text for run in p.runs)
        for k, v in datos.items():
            texto = texto.replace(f"{{{{{k}}}}}", str(v))
        for run in p.runs:
            run.text = ""
        if p.runs:
            p.runs[0].text = texto

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    texto = "".join(run.text for run in p.runs)
                    for k, v in datos.items():
                        texto = texto.replace(f"{{{{{k}}}}}", str(v))
                    for run in p.runs:
                        run.text = ""
                    if p.runs:
                        p.runs[0].text = texto


def generar_descarga(nombre, datos):
    ruta = os.path.join(PLANTILLAS, nombre)
    doc = Document(ruta)
    reemplazar(doc, datos)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
# ==========================================================
# MÓDULO PROCESOS
# ==========================================================
elif st.session_state.menu == "Procesos":

    st.markdown(
        f'<div class="banner-id">PROCESO ACTUAL: {ID}</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    ### 🔹 Flujo del Proceso
    1️⃣ Estudio Previo ➝  
    2️⃣ Compras ➝  
    3️⃣ Contratación
    """)

    # ==========================================================
    # ================= ETAPA 1 =================
    # ==========================================================
    st.header("ETAPA 1 — ESTUDIO PREVIO")

    objeto = st.text_area("OBJETO")
    necesidad = st.text_area("NECESIDAD")
    justificacion = st.text_area("JUSTIFICACIÓN")

    col1, col2 = st.columns(2)
    with col1:
        centro = st.text_input("CENTRO DE COSTOS")
    with col2:
        programa = st.text_input("PROGRAMA")

    col3, col4 = st.columns(2)
    with col3:
        rubro = st.text_input("RUBRO")
    with col4:
        codigo_planeacion = st.text_input("CÓDIGO PLANEACIÓN")

    caracteristicas = st.text_area("CARACTERÍSTICAS TÉCNICAS")

    forma_pago = st.text_input("FORMA DE PAGO")

    col5, col6 = st.columns(2)
    with col5:
        modalidad = st.selectbox(
            "MODALIDAD",
            ["Contratación Directa", "Invitación Privada", "Convocatoria Abierta"]
        )
    with col6:
        valor = st.number_input("VALOR", min_value=0, step=1000)

    plazo = st.number_input("PLAZO (Meses/Días)", min_value=1)

    valor_letras = num2words(valor, lang="es").upper() if valor else ""
    st.text_input("VALOR EN LETRAS", value=valor_letras, disabled=True)

    fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

    col_guardar, col_word = st.columns(2)

    with col_guardar:
        if st.button("💾 Guardar ETAPA 1", key="guardar_etapa1"):
            sheet = conectar_sheet()

            fila = [
                ID, objeto, necesidad, justificacion,
                centro, programa, rubro, codigo_planeacion,
                caracteristicas, forma_pago, modalidad,
                valor, valor_letras, plazo,
                str(fecha_estudio),
                "", "", "", "", "", "", "", "", "", ""
            ]

            sheet.append_row(fila)
            st.success("ETAPA 1 guardada correctamente.")

    with col_word:
        if st.button("📄 Generar Estudio Previo", key="word_estudio"):
            datos = {
                "ID_PROCESO": ID,
                "OBJETO": objeto,
                "NECESIDAD": necesidad,
                "JUSTIFICACION": justificacion,
                "VALOR": f"{valor:,.0f}".replace(",", "."),
                "VALOR_LETRAS": valor_letras,
                "PLAZO": plazo,
                "FECHA_ESTUDIO": fecha_estudio
            }

            archivo = generar_descarga("estudio_previo.docx", datos)

            st.download_button(
                "⬇ Descargar Estudio Previo",
                archivo,
                f"estudio_previo_{ID}.docx",
                key="down_estudio"
            )

    # ==========================================================
    # ================= ETAPA 2 =================
    # ==========================================================
    st.header("ETAPA 2 — ÁREA DE COMPRAS")

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

    if st.button("💾 Guardar ETAPA 2", key="guardar_etapa2"):
        sheet = conectar_sheet()
        fila_num = buscar_fila(sheet, ID)

        if fila_num:
            sheet.update(
                f"P{fila_num}:S{fila_num}",
                [[prop1, val1, prop2, val2]]
            )
            st.success("ETAPA 2 actualizada correctamente.")
        else:
            st.error("Debe guardar primero la ETAPA 1.")

    # ==========================================================
    # ================= ETAPA 3 =================
    # ==========================================================
    st.header("ETAPA 3 — CONTRATACIÓN")

    col1, col2, col3 = st.columns(3)

    with col1:
        tipo_contrato = st.selectbox(
            "TIPO DE CONTRATO",
            ["Obra", "Consultoría", "Prestación de Servicios",
             "Suministro", "Compraventa", "Arrendamiento"]
        )

    with col2:
        supervisor = st.text_input("SUPERVISOR")

    with col3:
        cdp = st.text_input("CDP")

    fecha_firma = st.date_input("FECHA FIRMA CONTRATO")

    col_guardar3, col_contrato = st.columns(2)

    with col_guardar3:
        if st.button("💾 Guardar ETAPA 3", key="guardar_etapa3"):
            sheet = conectar_sheet()
            fila_num = buscar_fila(sheet, ID)

            if fila_num:
                sheet.update(
                    f"T{fila_num}:W{fila_num}",
                    [[tipo_contrato, supervisor, cdp, str(fecha_firma)]]
                )
                st.success("ETAPA 3 actualizada correctamente.")
            else:
                st.error("Debe guardar primero la ETAPA 1.")

    with col_contrato:
        if st.button("📄 Generar Contrato", key="generar_contrato"):
            archivo = generar_descarga(
                "contrato.docx",
                {
                    "ID_PROCESO": ID,
                    "TIPO_CONTRATO": tipo_contrato,
                    "SUPERVISOR": supervisor,
                    "CDP": cdp,
                    "FECHA_FIRMA": fecha_firma
                }
            )

            st.download_button(
                "⬇ Descargar Contrato",
                archivo,
                f"contrato_{ID}.docx",
                key="down_contrato"
            )

    st.success("Sistema operativo correctamente.")
# ==========================================================
# MÓDULO CONTRATOS
# ==========================================================
elif st.session_state.menu == "Contratos":

    st.header("📜 MÓDULO DE CONTRATOS")

    sheet = conectar_sheet()
    registros = sheet.get_all_records()

    contratos_generados = [
        r for r in registros
        if r.get("TIPO_CONTRATO") not in [None, ""]
    ]

    if contratos_generados:

        st.success(f"Se encontraron {len(contratos_generados)} contratos generados.")

        for contrato in contratos_generados:

            with st.container():

                st.markdown(f"""
                ### 📄 Proceso {contrato.get('ID_PROCESO')}
                **Tipo:** {contrato.get('TIPO_CONTRATO')}  
                **Supervisor:** {contrato.get('SUPERVISOR')}  
                """)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        f"📂 Abrir {contrato.get('ID_PROCESO')}",
                        key=f"abrir_{contrato.get('ID_PROCESO')}"
                    ):
                        st.session_state.ID_PROCESO = contrato.get("ID_PROCESO")
                        st.session_state.menu = "Procesos"
                        st.rerun()

                with col2:
                    archivo = generar_descarga("contrato.docx", contrato)

                    st.download_button(
                        "⬇ Descargar Contrato",
                        archivo,
                        f"contrato_{contrato.get('ID_PROCESO')}.docx",
                        key=f"descargar_{contrato.get('ID_PROCESO')}"
                    )

                st.markdown("---")

    else:
        st.warning("No existen contratos generados aún.")


# ==========================================================
# MÓDULO REPORTES
# ==========================================================
elif st.session_state.menu == "Reportes":

    st.header("📊 MÓDULO DE REPORTES")

    sheet = conectar_sheet()
    registros = sheet.get_all_records()

    total_procesos = len(registros)

    contratos = [
        r for r in registros
        if r.get("TIPO_CONTRATO") not in [None, ""]
    ]

    total_contratos = len(contratos)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Procesos", total_procesos)

    with col2:
        st.metric("Total Contratos Generados", total_contratos)

    # Distribución por tipo
    tipos = {}
    for c in contratos:
        tipo = c.get("TIPO_CONTRATO")
        if tipo:
            tipos[tipo] = tipos.get(tipo, 0) + 1

    if tipos:
        st.subheader("Distribución por Tipo de Contrato")
        st.bar_chart(tipos)

    st.info("Módulo ampliable para estadísticas avanzadas.")


# ==========================================================
# MÓDULO CONFIGURACIÓN
# ==========================================================
elif st.session_state.menu == "Configuracion":

    st.header("⚙ CONFIGURACIÓN DEL SISTEMA")

    st.subheader("Gestión de Identificador")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Generar Nuevo ID", key="nuevo_id_config"):
            st.session_state.ID_PROCESO = generar_id()
            st.success(f"Nuevo ID generado: {st.session_state.ID_PROCESO}")

    with col2:
        if st.button("🧹 Limpiar Sesión", key="limpiar_sesion"):
            st.session_state.clear()
            st.success("Sesión limpiada correctamente.")
            st.rerun()

    st.markdown("---")

    st.subheader("Diagnóstico del Sistema")

    sheet = conectar_sheet()
    registros = sheet.get_all_records()

    st.write("Procesos registrados en la base:", len(registros))
    st.write("ID actual en sesión:", st.session_state.get("ID_PROCESO"))

    st.success("Sistema operativo correctamente.")
