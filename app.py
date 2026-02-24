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


def limpiar_valor(texto):
    texto = texto.replace("$", "").replace(",", "").strip()
    return int(texto) if texto.isdigit() else 0


def formatear_moneda(key):
    valor = st.session_state.get(key, "")
    limpio = valor.replace("$", "").replace(",", "").strip()
    if limpio.isdigit():
        numero = int(limpio)
        st.session_state[key] = f"$ {numero:,.0f}"
        return numero
    return 0


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
# ETAPA 1
# =====================================================
if etapa == "1 Estudio Previo":

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

        st.text_input("VALOR ($)", key="valor_ep", on_change=formatear_moneda, args=("valor_ep",))
        valor = formatear_moneda("valor_ep")

        if valor > 0:
            st.success(valor_en_letras(valor))

        plazo = st.number_input("PLAZO (días)", min_value=1)
        fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

        st.markdown('</div>', unsafe_allow_html=True)

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

                st.success("Proceso guardado correctamente.")
                st.session_state.ID_PROCESO = generar_id()

            except Exception as e:
                st.error(f"Error al guardar proceso: {e}")

# =====================================================
# ETAPA 2 — PLANEACIÓN
# =====================================================
if etapa == "2 Planeación":

    st.markdown("### ETAPA 2 — PLANEACIÓN")

    # -------- PROPONENTE 1 --------
    st.markdown("#### PROPONENTE 1")

    c1, c2, c3, c4 = st.columns([2,2,2,3])

    with c1:
        tipo1 = st.selectbox("TIPO PERSONA", ["Persona Natural", "Persona Jurídica"], key="tipo1")

    with c2:
        nombre1 = st.text_input("NOMBRE / RAZÓN SOCIAL", key="nombre1")

    with c3:
        id1 = st.text_input("N° CC" if tipo1=="Persona Natural" else "N° NIT", key="id1")

    with c4:
        st.text_input("VALOR PROPUESTA 1", key="valor1", on_change=formatear_moneda, args=("valor1",))

    valor1 = formatear_moneda("valor1")

    if valor1 > 0:
        st.success(valor_en_letras(valor1))

    st.divider()

    # -------- PROPONENTE 2 --------
    st.markdown("#### PROPONENTE 2")

    c5, c6, c7, c8 = st.columns([2,2,2,3])

    with c5:
        tipo2 = st.selectbox("TIPO PERSONA", ["Persona Natural", "Persona Jurídica"], key="tipo2")

    with c6:
        nombre2 = st.text_input("NOMBRE / RAZÓN SOCIAL", key="nombre2")

    with c7:
        id2 = st.text_input("N° CC" if tipo2=="Persona Natural" else "N° NIT", key="id2")

    with c8:
        st.text_input("VALOR PROPUESTA 2", key="valor2", on_change=formatear_moneda, args=("valor2",))

    valor2 = formatear_moneda("valor2")

    if valor2 > 0:
        st.success(valor_en_letras(valor2))

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
