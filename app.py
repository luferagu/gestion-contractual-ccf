import streamlit as st
from datetime import date
from num2words import num2words
from database import conectar_db

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    layout="wide",
    page_title="Sistema de Gestión Contractual",
    initial_sidebar_state="expanded"
)

# =====================================================
# ESTILOS CORPORATIVOS
# =====================================================
st.markdown("""
<style>
body { background-color: #0f172a; }
.main { background-color: #0f172a; }
.sidebar .sidebar-content { background-color: #111827; }
h1, h2, h3 { color: white; }
.block-container { padding-top: 2rem; }

.card {
    background-color: #1e293b;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.stepper {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.step {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    background-color: #1e293b;
    color: white;
}

.step.active { background-color: #2563eb; }

.banner-id {
    background: linear-gradient(90deg, #14532d, #166534);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    font-weight: bold;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.title("📂 CCF")
    st.markdown("---")
    st.button("🏠 Inicio")
    st.button("📁 Proceso")
    st.button("📑 Contratos")
    st.button("📊 Reportes")
    st.button("⚙ Configuración")
    st.markdown("---")
    st.button("Cerrar sesión")

# =====================================================
# FUNCIONES BASE
# =====================================================

def generar_id():
    conn = conectar_db()
    cursor = conn.cursor()
    year = date.today().year

    cursor.execute(
        "SELECT COUNT(*) FROM procesos WHERE id_proceso LIKE %s",
        (f"%-{year}",)
    )

    total = cursor.fetchone()[0]
    conn.close()
    return f"{total+1:03d}-{year}"


def proceso_existe(id_proceso):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM procesos WHERE id_proceso = %s",
        (id_proceso,)
    )
    existe = cursor.fetchone()
    conn.close()
    return existe is not None


def valor_en_letras(valor):
    if valor == 0:
        return ""
    texto = num2words(valor, lang="es")
    texto = texto.replace("uno", "un")
    return texto.upper() + " PESOS M/CTE"


def procesar_moneda(key):
    valor_texto = st.session_state.get(key, "")
    limpio = valor_texto.replace("$", "").replace(",", "").strip()

    if limpio.isdigit():
        numero = int(limpio)
        formateado = f"$ {numero:,.0f}"
        return numero, formateado

    return 0, ""


# =====================================================
# CONTROL DE ID
# =====================================================
if "ID_PROCESO" not in st.session_state:
    st.session_state.ID_PROCESO = generar_id()

ID = st.session_state.ID_PROCESO

# =====================================================
# NAVEGACIÓN ETAPAS
# =====================================================
etapa = st.radio(
    "",
    ["1 Estudio Previo", "2 Planeación", "3 Contratación", "4 Ejecución"],
    horizontal=True
)

st.markdown(f"""
<div class="banner-id">
ID_PROCESO generado automáticamente: {ID}
</div>
""", unsafe_allow_html=True)

# =====================================================
# ETAPA 1 — ESTUDIO PREVIO (AJUSTADA Y ORDENADA)
# =====================================================
if etapa == "1 Estudio Previo":

    st.markdown("### ETAPA 1 — ESTUDIO PREVIO")

    # =====================================================
    # CAMPOS PRINCIPALES (ANCHO COMPLETO)
    # =====================================================

    objeto = st.text_area(
        "OBJETO",
        height=200,
        placeholder="Describa el objeto contractual"
    )

    justificacion = st.text_area(
        "JUSTIFICACIÓN",
        height=200,
        placeholder="Fundamente técnica, jurídica y financieramente el proceso"
    )

    necesidad = st.text_area(
        "1. DESCRIPCIÓN DE LA NECESIDAD QUE LA ENTIDAD PRETENDE SATISFACER CON LA CONTRATACIÓN",
        height=220,
        placeholder="Describa la necesidad que se pretende satisfacer"
    )

    # =====================================================
    # BLOQUE ECONÓMICO (DEBAJO DE LA NECESIDAD)
    # =====================================================

    st.markdown("### INFORMACIÓN ECONÓMICA Y PLAZO")

    col1, col2, col3 = st.columns([2,1,1])

    with col1:
        st.text_input(
            "VALOR ($)",
            key="valor_ep",
            placeholder="Ej: 25,000,000"
        )

        valor, _ = procesar_moneda("valor_ep")

        if valor > 0:
            st.success(valor_en_letras(valor))
            valor_letras = valor_en_letras(valor)
        else:
            valor_letras = ""

    with col2:
        plazo = st.number_input(
            "PLAZO",
            min_value=1,
            value=1
        )

    with col3:
        unidad_plazo = st.selectbox(
            "UNIDAD",
            ["Días", "Meses"]
        )

    fecha_estudio = st.date_input(
        "FECHA ESTUDIO",
        value=date.today()
    )

    st.markdown("---")

    # =====================================================
    # INFORMACIÓN PRESUPUESTAL Y PLANEACIÓN
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        centro_costos = st.text_input("CENTRO DE COSTOS")

    with c2:
        programa = st.text_input("PROGRAMA")

    with c3:
        codigo_planeacion = st.text_input("ACTIVIDAD DE PLANEACIÓN")

    with c4:
        rubro = st.text_input("RUBRO")

    # =====================================================
    # 2. DESCRIPCIÓN DEL OBJETO
    # =====================================================

    st.markdown("## 2. DESCRIPCIÓN DEL OBJETO A CONTRATAR, CON SUS ESPECIFICACIONES")

    objeto_detallado = st.text_area(
        "2.1 OBJETO (DESCRIPCIÓN DETALLADA)",
        height=150
    )

    caracteristicas_tecnicas = st.text_area(
        "2.2 CARACTERÍSTICAS TÉCNICAS DEL BIEN",
        height=150
    )

       # =====================================================
    # 2.3 FUNDAMENTOS JURÍDICOS
    # =====================================================

    st.markdown("### 2.3 FUNDAMENTOS JURÍDICOS")

    col_modalidad, col_articulo, col_numeral, col_literal = st.columns(4)

    # ---------------- MODALIDAD ----------------
    with col_modalidad:
        modalidad = st.selectbox(
            "MODALIDAD DE CONTRATACIÓN",
            ["DIRECTA", "PRIVADA", "CONVOCATORIA ABIERTA"],
            key="modalidad_unica"
        )

    # ---------------- ARTÍCULO AUTOMÁTICO + NUMERALES ----------------
    if modalidad == "DIRECTA":
        articulo = "ARTÍCULO 16"
        opciones_numeral = ["1", "2", "3"]

    elif modalidad == "PRIVADA":
        articulo = "ARTÍCULO 17"
        opciones_numeral = ["1", "2", "3", "4"]

    else:
        articulo = "ARTÍCULO 18"
        opciones_numeral = ["1", "2", "3"]

    # ---------------- ARTÍCULO (DINÁMICO Y ALINEADO) ----------------
    with col_articulo:
        st.text_input(
            "ARTÍCULO",
            value=articulo,
            disabled=True
        )

    # ---------------- NUMERAL DINÁMICO ----------------
    with col_numeral:
        numeral = st.selectbox(
            "NUMERAL",
            opciones_numeral,
            key="numeral_dinamico"
        )

    # ---------------- LITERAL CONDICIONAL ESTRICTO ----------------
    with col_literal:

        if modalidad == "DIRECTA" and numeral == "2":

            literal = st.selectbox(
                "LITERAL",
                ["a", "b", "c", "d", "e", "f", "g", "h"],
                key="literal_dinamico"
            )

        else:
            literal = None
            st.text_input(
                "LITERAL",
                value="No aplica",
                disabled=True
            )

    # 🔹 CIERRE VISUAL DEL BLOQUE
    st.markdown("---")

    # =====================================================
    # 3. CONDICIONES DEL FUTURO CONTRATO
    # =====================================================

    st.markdown("## 3. CONDICIONES DEL FUTURO CONTRATO")

   # ---------------- 3.1 OPORTUNIDAD ----------------
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    
    oportunidad = st.multiselect(
        "3.1 OPORTUNIDAD (Mes de suscripción)",
        meses,
        key="meses_suscripcion"
    )
    
    # Mostrar texto consolidado si selecciona meses
    if oportunidad:
        texto_oportunidad = ", ".join(oportunidad)
        st.info(f"El contrato se deberá suscribir en el mes de {texto_oportunidad} de 2026.")

# ---------------- 3.2 PLAZO Y VIGENCIA DE EJECUCIÓN ----------------

if plazo and unidad_plazo:
    texto_plazo = f"{plazo} {unidad_plazo.lower()}"
    
    st.text_area(
        "3.2 PLAZO Y VIGENCIA DE EJECUCIÓN",
        value=f"El término de duración del presente contrato será de {texto_plazo}, contados a partir del acta de inicio.",
        disabled=True,
        height=100
    )

    forma_pago = st.text_area(
        "3.3 FORMA DE PAGO",
        height=120
    )

    analisis = st.text_area(
        "3.4 ANÁLISIS DE LAS CONDICIONES Y PRECIOS DEL MERCADO (Literal)",
        height=120
    )

       # =====================================================
    # 5. IDENTIFICACIÓN DEL RIESGO Y GARANTÍAS
    # =====================================================

    st.markdown("## 5. IDENTIFICACIÓN DEL RIESGO Y GARANTÍAS")

    opciones_garantias = {
        "Anticipo": """1. Anticipo: Para garantizar el Buen manejo y Correcta Inversión del Anticipo, por la suma equivalente al cien por cien (100%) del mismo, por el término del contrato de ejecución contractual y seis (6) meses más.""",

        "Cumplimiento": """2. Cumplimiento: Para precaver los perjuicios derivados del incumplimiento del contrato, por un valor equivalente al veinte (20%) del valor del mismo y con una vigencia igual al término de ejecución contractual y seis (6) meses más.""",

        "Salarios y Prestaciones": """3. Salarios, Prestaciones Sociales e Indemnizaciones: Para cubrir el riesgo de incumplimiento de las obligaciones laborales, de acuerdo con lo consagrado en el artículo 64 del Código Sustantivo de Trabajo, a que esté obligado el afianzado y relacionadas con el personal utilizado para la ejecución del contrato, por un valor equivalente al quince por ciento (15%) del contrato y por una vigencia igual al término del contrato y tres (3) años más.""",

        "Responsabilidad Civil Extracontractual": """4. Responsabilidad Civil Extracontractual: Para indemnizar los perjuicios patrimoniales que se causen por el Contratista a la salud o bienes de terceros, por los doscientos salarios mínimos mensuales vigentes (200 SMLMV) y una vigencia igual al término del mismo.""",

        "Estabilidad de la Obra": """5. Estabilidad y Conservación de la Obra Ejecutada: En cuantía equivalente al veinte por ciento (20%), del valor del contrato y con una vigencia de cinco (5) años contados a partir del recibo a entera satisfacción de las obras civiles objeto del contrato.""",

        "Calidad del Servicio": """6. Calidad de los Elementos o Servicios: De las especificaciones técnicas contractuales que determinan la calidad del elemento o servicio contratado. El cual deberá constituirse por el treinta (30%) del valor del contrato, que cubra el término del mismo y un año más."""
    }

    garantias_seleccionadas = st.multiselect(
        "GARANTÍAS EXIGIDAS",
        list(opciones_garantias.keys()),
        key="garantias_select"
    )

    if garantias_seleccionadas:
        texto_garantias = "\n\n".join(
            [opciones_garantias[g] for g in garantias_seleccionadas]
        )

        st.text_area(
            "Detalle de Garantías Seleccionadas",
            value=texto_garantias,
            height=300,
            disabled=True
        )

    # =====================================================
    # GUARDAR (LÓGICA ORIGINAL)
    # =====================================================

    st.markdown("---")

    if st.button("GUARDAR ESTUDIO PREVIO", use_container_width=True):

        if proceso_existe(ID):
            st.warning("Este proceso ya está registrado.")
        else:
            try:
                conn = conectar_db()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO procesos
                    (id_proceso, objeto, necesidad, justificacion, valor, plazo, fecha_estudio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    ID,
                    objeto,
                    necesidad,
                    justificacion,
                    valor,
                    plazo,
                    fecha_estudio
                ))

                conn.commit()
                conn.close()

                st.success("Proceso guardado correctamente.")
                st.session_state.ID_PROCESO = generar_id()

            except Exception as e:
                st.error(f"Error al guardar proceso: {e}")

# =====================================================
# ETAPA 2 — PLANEACIÓN
# =====================================================
if etapa == "2 Planeación":

    st.markdown("### ETAPA 2 — PLANEACIÓN")

    # =================================================
    # PROPONENTE 1
    # =================================================
    st.markdown("#### PROPONENTE 1")

    c1, c2, c3, c4 = st.columns([2,2,2,3])

    with c1:
        tipo1 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo1"
        )

    with c2:
        nombre1 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre1"
        )

    with c3:
        id1 = st.text_input(
            "N° CC" if tipo1 == "Persona Natural" else "N° NIT",
            key="id1"
        )

    with c4:
        st.text_input("VALOR PROPUESTA 1", key="valor1")

    valor1, valor1_formateado = procesar_moneda("valor1")

    if valor1 > 0:
        st.write("Valor formateado:", valor1_formateado)
        st.success(valor_en_letras(valor1))

    # ---- REPRESENTANTE LEGAL (SOLO SI ES JURÍDICA) ----
    if tipo1 == "Persona Jurídica":

        st.markdown("##### REPRESENTANTE LEGAL — PROPONENTE 1")

        rl1_col1, rl1_col2 = st.columns(2)

        with rl1_col1:
            representante1 = st.text_input(
                "NOMBRE DEL REPRESENTANTE LEGAL",
                key="rep1"
            )

        with rl1_col2:
            cc_rep1 = st.text_input(
                "N° CC REPRESENTANTE LEGAL",
                key="cc_rep1"
            )

    st.divider()

    # =================================================
    # PROPONENTE 2
    # =================================================
    st.markdown("#### PROPONENTE 2")

    c5, c6, c7, c8 = st.columns([2,2,2,3])

    with c5:
        tipo2 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo2"
        )

    with c6:
        nombre2 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre2"
        )

    with c7:
        id2 = st.text_input(
            "N° CC" if tipo2 == "Persona Natural" else "N° NIT",
            key="id2"
        )

    with c8:
        st.text_input("VALOR PROPUESTA 2", key="valor2")

    valor2, valor2_formateado = procesar_moneda("valor2")

    if valor2 > 0:
        st.write("Valor formateado:", valor2_formateado)
        st.success(valor_en_letras(valor2))

    # ---- REPRESENTANTE LEGAL (SOLO SI ES JURÍDICA) ----
    if tipo2 == "Persona Jurídica":

        st.markdown("##### REPRESENTANTE LEGAL — PROPONENTE 2")

        rl2_col1, rl2_col2 = st.columns(2)

        with rl2_col1:
            representante2 = st.text_input(
                "NOMBRE DEL REPRESENTANTE LEGAL",
                key="rep2"
            )

        with rl2_col2:
            cc_rep2 = st.text_input(
                "N° CC REPRESENTANTE LEGAL",
                key="cc_rep2"
            )

# =====================================================
# ETAPA 3 — CONTRATACIÓN
# =====================================================
if etapa == "3 Contratación":

    st.markdown("### ETAPA 3 — CONTRATOS")

    tipo = st.selectbox("TIPO CONTRATO",
        ["Obra", "Consultoría", "Prestación de Servicios", "Suministro"])

    supervisor = st.text_input("SUPERVISOR")
    cdp = st.text_input("CDP")
    fecha_firma = st.date_input("FECHA FIRMA")

    if st.button("GUARDAR CONTRATO"):

        if not proceso_existe(ID):
            st.error("Debe guardar primero el Estudio Previo.")
        else:
            try:
                conn = conectar_db()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO contratos
                    (id_proceso, tipo_contrato, supervisor, cdp, fecha_firma)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    ID,
                    tipo,
                    supervisor,
                    cdp,
                    fecha_firma
                ))

                conn.commit()
                conn.close()

                st.success("Contrato guardado correctamente.")

            except Exception as e:
                st.error(f"Error al guardar contrato: {e}")

# =====================================================
# FINAL
# =====================================================
st.divider()
st.success("Sistema operativo en PostgreSQL (Supabase).")























