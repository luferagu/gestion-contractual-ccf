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

body {
    background-color: #0f172a;
}

.main {
    background-color: #0f172a;
}

.sidebar .sidebar-content {
    background-color: #111827;
}

h1, h2, h3 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: #1e293b;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.stepper {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
}

.step {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    background-color: #1e293b;
    color: white;
}

.step.active {
    background-color: #2563eb;
}

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


def limpiar_valor(texto):
    texto = texto.replace("$", "").replace(",", "").strip()
    return int(texto) if texto.isdigit() else 0


# =====================================================
# CONTROL DE ID EN SESIÓN
# =====================================================
if "ID_PROCESO" not in st.session_state:
    st.session_state.ID_PROCESO = generar_id()

ID = st.session_state.ID_PROCESO

# =====================================================
# ENCABEZADO PRINCIPAL
# =====================================================
st.markdown("## SISTEMA DE GESTIÓN CONTRACTUAL – CCF")

st.markdown("""
<div class="stepper">
<div class="step active">1 Estudio Previo</div>
<div class="step">2 Planeación</div>
<div class="step">3 Contratación</div>
<div class="step">4 Ejecución</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="banner-id">
ID_PROCESO generado automáticamente: {ID}
</div>
""", unsafe_allow_html=True)

# =====================================================
# ETAPA 1 — ESTUDIO PREVIO
# =====================================================
st.markdown("### ETAPA 1 — ESTUDIO PREVIO")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    objeto = st.text_area("OBJETO")
    necesidad = st.text_area("NECESIDAD")
    justificacion = st.text_area("JUSTIFICACIÓN")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    valor_input = st.text_input("VALOR ($)")
    valor = limpiar_valor(valor_input)

    if valor > 0:
        st.success(valor_en_letras(valor))

    plazo = st.number_input("PLAZO (días)", min_value=1)
    fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- GUARDAR PROCESO ----------
if st.button("GUARDAR ESTUDIO PREVIO"):

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

            st.success("Proceso guardado correctamente en PostgreSQL.")
            st.session_state.ID_PROCESO = generar_id()

        except Exception as e:
            st.error(f"Error al guardar proceso: {e}")

# =====================================================
# ETAPA 3 — CONTRATOS
# =====================================================
st.markdown("### ETAPA 3 — CONTRATOS")

st.markdown('<div class="card">', unsafe_allow_html=True)

tipo = st.selectbox("TIPO CONTRATO",
    ["Obra", "Consultoría", "Prestación de Servicios", "Suministro"])

supervisor = st.text_input("SUPERVISOR")
cdp = st.text_input("CDP")
fecha_firma = st.date_input("FECHA FIRMA")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- GUARDAR CONTRATO ----------
if st.button("GUARDAR CONTRATO"):

    if not proceso_existe(ID):
        st.error("Debe guardar primero el Estudio Previo antes de registrar el contrato.")
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

            st.success("Contrato guardado correctamente en PostgreSQL.")

        except Exception as e:
            st.error(f"Error al guardar contrato: {e}")

# =====================================================
# FINAL
# =====================================================
st.divider()
st.success("Sistema operativo en PostgreSQL (Supabase).")
