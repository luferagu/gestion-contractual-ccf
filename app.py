import streamlit as st
from datetime import date
from num2words import num2words
from database import conectar_db
from convertir_rubros import datos_rubros
from actividades_planeacion import actividades_planeacion


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
    return texto.upper() + " DE PESOS M/CTE"


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
# FUNCIONES DE RENDERIZADO POR ETAPA
# =====================================================

def render_estudio_previo():
    st.markdown("### ETAPA 1 — ESTUDIO PREVIO")
    st.info("Contenido del Estudio Previo aquí.")


def render_planeacion():

    st.markdown("### ETAPA 2 — PLANEACIÓN")

    # =====================================================
    # PROPONENTE 1
    # =====================================================

    st.markdown("#### PROPONENTE 1")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

    with col1:
        tipo1 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo1"
        )

    with col2:
        nombre1 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre1"
        )

    with col3:
        identificacion1 = st.text_input(
            "N° CC" if tipo1 == "Persona Natural" else "N° NIT",
            key="id1"
        )

    with col4:
        st.text_input("VALOR PROPUESTA 1", key="valor1")

    valor1, valor1_formateado = procesar_moneda("valor1")

    if valor1 > 0:
        st.write("Valor formateado:", valor1_formateado)
        st.success(valor_en_letras(valor1))

    representante1 = None
    cc_rep1 = None

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

    # =====================================================
    # PROPONENTE 2
    # =====================================================

    st.markdown("#### PROPONENTE 2")

    col5, col6, col7, col8 = st.columns([2, 2, 2, 3])

    with col5:
        tipo2 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo2"
        )

    with col6:
        nombre2 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre2"
        )

    with col7:
        identificacion2 = st.text_input(
            "N° CC" if tipo2 == "Persona Natural" else "N° NIT",
            key="id2"
        )

    with col8:
        st.text_input("VALOR PROPUESTA 2", key="valor2")

    valor2, valor2_formateado = procesar_moneda("valor2")

    if valor2 > 0:
        st.write("Valor formateado:", valor2_formateado)
        st.success(valor_en_letras(valor2))

    representante2 = None
    cc_rep2 = None

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

    st.markdown("---")


def render_contratacion():
    st.markdown("### ETAPA 3 — CONTRATACIÓN")
    st.info("Contenido de contratación aquí.")


def render_ejecucion():
    st.markdown("### ETAPA 4 — EJECUCIÓN")
    st.info("Contenido de ejecución aquí.")


# =====================================================
# ENRUTADOR DE ETAPAS
# =====================================================

if etapa == "1 Estudio Previo":
    render_estudio_previo()

elif etapa == "2 Planeación":
    render_planeacion()

elif etapa == "3 Contratación":
    render_contratacion()

elif etapa == "4 Ejecución":
    render_ejecucion()

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
        placeholder="Describa el objeto contractual",
        key="objeto_principal"
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
    # BLOQUE ECONÓMICO
    # =====================================================

    st.markdown("### INFORMACIÓN ECONÓMICA Y PLAZO")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.text_input(
            "VALOR ($)",
            key="valor_ep",
            placeholder="Ej: 25,000,000"
        )

        valor, _ = procesar_moneda("valor_ep")

        if valor > 0:
            st.success(valor_en_letras(valor))

    with col2:
        plazo = st.number_input("PLAZO", min_value=1, value=1)

    with col3:
        unidad_plazo = st.selectbox("UNIDAD", ["Días", "Meses"])

    fecha_estudio = st.date_input("FECHA ESTUDIO", value=date.today())

    st.markdown("---")

    # =====================================================
    # TIPO DE PRESUPUESTO
    # =====================================================

    st.markdown("### PRESUPUESTO")

    presupuesto_tipo = st.radio(
        "",
        ["FUNCIONAMIENTO", "INVERSIÓN", "PAT"],
        horizontal=True,
        key="tipo_presupuesto"
    )

    st.markdown("---")
    # =====================================================
    # INFORMACIÓN PRESUPUESTAL (COMPLETA Y CONSOLIDADA)
    # =====================================================

    estructura_presupuestal = {

        "4100": {
            "nombre": "REGISTROS PUBLICOS",
            "programas": {
                "4100-4110": "FUNCIONAMIENTO SISTEMAS",
                "4100-4111": "BRIGADAS DE REGISTRO",
                "4100-4112": "COSTUBRE MERCANTIL",
                "4100-4113": "BRIGADA DE REGISTRO DE PROPONENTES",
                "4100-4114": "JORNADAS DE RENOVACIONES",
                "4100-4115": "CONFERENCIAS TALLER",
                "4100-4116": "REVISORIA FISCAL",
                "4100-4117": "PARTE TECNICA PROYECTO RUE",
                "4100-4118": "PROYECTO COMUNICACIONES",
                "4100-4119": "OTRAS NECESIDADES DE SISTEMAS",
                "4100-4120": "NOMINA",
                "4100-4121": "FUNCIONAMIENTO FACA",
                "4100-4122": "FUNCIONAMIENTO FUNZA",
                "4100-4123": "FUNCIONAMIENTO VILLETA",
                "4100-4124": "FUNCIONAMIENTO PACHO",
                "4100-4125": "FUNCIONAMIENTO GENERAL",
                "4100-4126": "LISTA CONTRALORES Y PERITOS"
            }
        },

        "4120": {"nombre": "NOMINA JURIDICA", "programas": {}},

        "4200": {
            "nombre": "MASC - METODOS ALTERNATIVOS DE SOLUCION",
            "programas": {
                "4200-4210": "CURSO FORMACION DE CONCILIADORES",
                "4200-4211": "EDUCACION CONTINUADA",
                "4200-4212": "SERVICIO SOCIAL DEL CENTRO DE CONCILIACION",
                "4200-4213": "PLEGABLES INFORMATIVOS",
                "4200-4214": "SEMINARIO TALLER CAPACITACION",
                "4200-4215": "JORNADA CONCILIACION ESCOLAR",
                "4200-4216": "NOMINA",
                "4200-4217": "FUNCIONAMIENTO MASC",
                "4200-4218": "SERVICIO DE CONCILIACION Y ARBITRAJE",
                "4200-4220": "INVESTIGACION",
                "4200-4221": "CURSO DE FORMACION DE CONCILIADORES PRIV"
            }
        },

        "4201": {"nombre": "METODOS ALTERNATIVO SOL Y CON", "programas": {}},

        "4300": {
            "nombre": "CIVICOS, SOCIALES Y CULTURALES",
            "programas": {
                "4300-4310": "DESARROLLO CULTURAL, DEPORTIVO Y SOCIAL",
                "4300-4311": "PROMOCION A LA GESTION CIVICA SOCIAL",
                "4300-4312": "ACTIVIDADES CULTURALES DEPORTIVAS",
                "4300-4313": "NOMINA",
                "4300-4314": "FUNCIONAMIENTO",
                "4300-4317": "CONSTRUYENDO FUTURO",
                "4300-4320": "CONSULTORIO JURIDICO",
                "4300-4321": "ELECCION DE GREMIOS"
            }
        },

        "4400": {
            "nombre": "MEJORAMIENTO DEL ENTORNO",
            "programas": {
                "4400-4410": "VEEDURIAS",
                "4400-4411": "CENSO",
                "4400-4412": "NOMINA",
                "4400-4413": "FUNCIONAMIENTO",
                "4400-4414": "ESTUDIOS E INVESTIGACIONES",
                "4400-4415": "MEJORAMIENTO Y CONSERVACION DEL MEDIO",
                "4400-4416": "SEGURIDAD, CONVIVENCIA Y PROMOCION CIUDADANA",
                "4400-4417": "GESTION Y FORTALECIMIENTO A LA COMPETITIVIDAD EMPRESARIAL",
                "4400-4418": "PROGRAMA DE INTERNACIONALIZACION",
                "4400-4420": "VEEDURIAS CIUDADANAS"
            }
        },

        "4500": {
            "nombre": "DESARROLLO EMPRESARIAL",
            "programas": {
                "4500-4510": "FERIAS, RUEDAS Y EVENTOS",
                "4500-4511": "FERIAS CAMARA DE FACATATIVA",
                "4500-4512": "OBLIGACIONES TRIBUTARIAS",
                "4500-4513": "CAPACITACION",
                "4500-4514": "LUSTRABOTAS",
                "4500-4515": "PANADEROS",
                "4500-4516": "SALONES DE BELLEZA",
                "4500-4517": "FORTALECIMIENTO SECTOR TURISTICO",
                "4500-4518": "PROYECTO AGRO ECO TURISTICO",
                "4500-4519": "MEGA PROYECTO INDUSTRIAL",
                "4500-4520": "RUEDA DE NEGOCIOS",
                "4500-4521": "APORTES Y CONTRIBUCIONES",
                "4500-4522": "CARTILLA INFORMATIVA",
                "4500-4523": "SEGUNDA EMISION CARTILLA TENDERO",
                "4500-4524": "SUSCRIPCION CONVENIOS",
                "4500-4525": "CENTRO DE ATENCION EMPRESARIAL",
                "4500-4526": "NOMINA",
                "4500-4527": "FUNCIONAMIENTO",
                "4500-4528": "PROMOCION Y APOYO EMPRENDIMIENTO",
                "4500-4529": "APOYO DESARROLLO AGROINDUSTRIAL",
                "4500-4530": "GESTION DE PROYECTOS",
                "4500-4531": "PROGRAMA DE INNOVACION",
                "4500-4532": "NOMINA GESTION PROYECTOS"
            }
        },

        "4600": {
            "nombre": "PROMOCION DEL COMERCIO",
            "programas": {
                "4600-4609": "FERIAS, RUEDAS, MISIONES Y ENCUENTROS",
                "4600-4610": "CAMPANAS COMERCIALES",
                "4600-4611": "NOMINA",
                "4600-4612": "FUNCIONAMIENTO"
            }
        },

        "4700": {
            "nombre": "GESTION ESTRATEGICA",
            "programas": {
                "4700-4704": "FUNCIONAMIENTO CONTROL INTERNO",
                "4700-4705": "GESTION DE CALIDAD",
                "4700-4707": "CONTROL INTERNO",
                "4700-4708": "PLANEACION INSTITUCIONAL",
                "4700-4709": "GESTION DOCUMENTAL",
                "4700-4710": "PROMOCION INSTITUCIONAL E IMAGEN CORPORATIVA",
                "4700-4711": "CAMPANA AFILIACION MTTO Y EVENTOS AFILIADOS",
                "4700-4712": "ELABORACION DE CREDENCIALES",
                "4700-4713": "ELABORACION PORTAFOLIO AFILIADOS",
                "4700-4714": "NOMINA",
                "4700-4715": "FUNCIONAMIENTO PRESIDENCIA EJECUTIVA",
                "4700-4716": "FUNCIONAMIENTO JUNTA DIRECTIVA PUBLICO",
                "4700-4720": "FORMACION EMPRESARIAL",
                "4700-4721": "HOJAS VERDES",
                "4700-4726": "FUNCIONAMIENTO JUNTA DIRECTIVA PRIVADO"
            }
        },

        "4800": {
            "nombre": "GESTION ADMINISTRATIVA",
            "programas": {
                "4800-4806": "NOMINA APRENDIZ SENA",
                "4800-4807": "FUNCIONAMIENTO TALENTO HUMANO",
                "4800-4809": "GESTION DEL TALENTO HUMANO",
                "4800-4810": "NOMINA",
                "4800-4811": "FUNCIONAMIENTO GENERAL PUBLICO",
                "4800-4812": "FUNCIONAMIENTO FUNZA",
                "4800-4813": "FUNCIONAMIENTO VILLETA",
                "4800-4814": "FUNCIONAMIENTO PACHO",
                "4800-4815": "JURIDICA",
                "4800-4816": "GESTION INFRAESTRUCTURA FISICA",
                "4800-4821": "FUNCIONAMIENTO GENERAL PRIVADO",
                "4800-4890": "INVERSION PUBLICA",
                "4800-4892": "INVERSION PRIVADA"
            }
        },

        "9999": {
            "nombre": "OTROS",
            "programas": {
                "9999-9999": "OTROS NO CODIFICADOS"
            }
        }
    }

# ===================== FILA 1 =====================
col1, col2 = st.columns(2)

with col1:

    if "estructura_presupuestal" in globals() and estructura_presupuestal:

        centro_label = st.selectbox(
            "CENTRO DE COSTOS",
            [f"{c} - {d['nombre']}" for c, d in estructura_presupuestal.items()],
            key="centro_costos_select"
        )

        centro_codigo = centro_label.split(" - ")[0]

    else:
        centro_label = None
        centro_codigo = None

        st.selectbox(
            "CENTRO DE COSTOS",
            ["No disponible"],
            disabled=True
        )

with col2:
    programas = estructura_presupuestal[centro_codigo]["programas"]

    if programas:
        programa_label = st.selectbox(
            "PROGRAMA",
            [f"{c} - {n}" for c, n in programas.items()],
            key="programa_select"
        )
        programa_codigo = programa_label.split(" - ")[0]
    else:
        programa_label = None
        programa_codigo = None
        st.selectbox("PROGRAMA", ["NO APLICA"], disabled=True)


# ===================== FILA 2 =====================
col3, col4 = st.columns(2)

# ===================== COLUMNA 4 — RUBRO =====================
with col4:

    if programa_codigo:

        # Filtrar rubros según programa seleccionado
        rubros_filtrados = [
            f"{rubro} - {descripcion}"
            for prog, rubro, descripcion in datos_rubros
            if prog == programa_codigo
        ]

        if rubros_filtrados:
            rubro_label = st.selectbox(
                "RUBRO",
                rubros_filtrados,
                key="rubro_select"
            )
            rubro_codigo = rubro_label.split(" - ")[0]
        else:
            rubro_label = None
            rubro_codigo = None
            st.selectbox(
                "RUBRO",
                ["No hay rubros disponibles para este programa"],
                disabled=True
            )

    else:
        rubro_label = None
        rubro_codigo = None
        st.selectbox(
            "RUBRO",
            ["Seleccione primero un programa"],
            disabled=True
        )

# ===================== COLUMNA 3 — ACTIVIDAD =====================
with col3:

    if presupuesto_tipo == "INVERSIÓN" and programa_codigo and rubro_codigo:

        actividades_filtradas = [
            f"{codigo} - {descripcion}"
            for prog, rub, codigo, descripcion in actividades_planeacion
            if prog == programa_codigo and rub == rubro_codigo
        ]

        if actividades_filtradas:
            actividad_planeacion = st.selectbox(
                "ACTIVIDAD DE PLANEACIÓN",
                actividades_filtradas,
                key="actividad_planeacion"
            )
        else:
            st.selectbox(
                "ACTIVIDAD DE PLANEACIÓN",
                ["No hay actividades asociadas"],
                disabled=True
            )

    else:
        st.text_input(
            "ACTIVIDAD DE PLANEACIÓN",
            value="No aplica",
            disabled=True
        )
# =====================================================
# SEPARADOR VISUAL (FUERA DE COLUMNAS)
# =====================================================

st.divider()

# =====================================================
# 2. DESCRIPCIÓN DEL OBJETO (ANCHO COMPLETO)
# =====================================================

st.markdown("## 2. DESCRIPCIÓN DEL OBJETO A CONTRATAR, CON SUS ESPECIFICACIONES")

st.text_area(
    "2.1 OBJETO (DESCRIPCIÓN DETALLADA)",
    value=objeto,
    height=150,
    disabled=True
)

caracteristicas_tecnicas = st.text_area(
    "2.2 CARACTERÍSTICAS TÉCNICAS DEL BIEN",
    height=150
)
    # =====================================================
    # 2.3 FUNDAMENTOS JURÍDICOS
    # =====================================================

# =====================================================
# 2.3 FUNDAMENTOS JURÍDICOS
# =====================================================

st.markdown("### 2.3 FUNDAMENTOS JURÍDICOS")

# Inicialización de estados
if "articulo_auto" not in st.session_state:
    st.session_state.articulo_auto = "ARTÍCULO 16"

if "numeral_dinamico" not in st.session_state:
    st.session_state.numeral_dinamico = "1"

if "literal_dinamico" not in st.session_state:
    st.session_state.literal_dinamico = "a"

# Columnas
col_modalidad, col_articulo, col_numeral, col_literal = st.columns(4)

with col_modalidad:
    modalidad = st.selectbox(
        "MODALIDAD DE CONTRATACIÓN",
        ["DIRECTA", "PRIVADA", "CONVOCATORIA ABIERTA"],
        key="modalidad_unica"
    )

# Lógica dinámica según modalidad
if modalidad == "DIRECTA":
    st.session_state.articulo_auto = "ARTÍCULO 16"
    opciones_numeral = ["1", "2", "3"]

elif modalidad == "PRIVADA":
    st.session_state.articulo_auto = "ARTÍCULO 17"
    opciones_numeral = ["1", "2", "3", "4"]

else:
    st.session_state.articulo_auto = "ARTÍCULO 18"
    opciones_numeral = ["1", "2", "3"]

# Validación del numeral actual
if st.session_state.numeral_dinamico not in opciones_numeral:
    st.session_state.numeral_dinamico = opciones_numeral[0]

with col_articulo:
    st.text_input(
        "ARTÍCULO",
        key="articulo_auto",
        disabled=True
    )

with col_numeral:
    numeral = st.selectbox(
        "NUMERAL",
        opciones_numeral,
        key="numeral_dinamico"
    )

with col_literal:
    if modalidad == "DIRECTA" and numeral == "2":
        literal = st.selectbox(
            "LITERAL",
            ["a", "b", "c", "d", "e", "f", "g", "h"],
            key="literal_dinamico"
        )
    else:
        st.text_input(
            "LITERAL",
            value="No aplica",
            disabled=True
        )

st.markdown("---")

# =====================================================
# 3. CONDICIONES DEL FUTURO CONTRATO
# =====================================================

st.markdown("## 3. CONDICIONES DEL FUTURO CONTRATO")

meses = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

meses_seleccionados = st.multiselect(
    "3.1 OPORTUNIDAD (Mes de suscripción en 2026)",
    meses,
    max_selections=2
)

if meses_seleccionados:
    oportunidad = " y ".join(meses_seleccionados) + " de 2026"
    st.success(f"Suscripción prevista para: {oportunidad}")

forma_pago = st.text_area(
    "3.3 FORMA DE PAGO",
    height=120
)

analisis = st.text_area(
    "3.4 ANÁLISIS DE LAS CONDICIONES Y PRECIOS DEL MERCADO",
    height=120
)

st.markdown("---")

    # =====================================================
# 5. IDENTIFICACIÓN DEL RIESGO Y GARANTÍAS
# =====================================================

st.markdown("## 5. IDENTIFICACIÓN DEL RIESGO Y GARANTÍAS")

opciones_garantias = {
    "Anticipo": """1. Anticipo: Para garantizar el Buen manejo y Correcta Inversión del Anticipo, por el 100% del mismo.""",
    "Cumplimiento": """2. Cumplimiento: Por el 20% del valor del contrato.""",
    "Salarios y Prestaciones": """3. Salarios y Prestaciones: Por el 15% del contrato.""",
    "Responsabilidad Civil Extracontractual": """4. Responsabilidad Civil Extracontractual: 200 SMLMV.""",
    "Estabilidad de la Obra": """5. Estabilidad de la Obra: 20% por 5 años.""",
    "Calidad del Servicio": """6. Calidad del Servicio: 30% con vigencia adicional."""
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

st.markdown("---")

# =====================================================
# GUARDAR
# =====================================================

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

        except Exception as e:
            st.error(f"Error al guardar proceso: {e}")


# =====================================================
# ETAPA 2 — PLANEACIÓN
# =====================================================

if etapa == "2 Planeación":

    st.markdown("### ETAPA 2 — PLANEACIÓN")

    # =====================================================
    # PROPONENTE 1
    # =====================================================

    st.markdown("#### PROPONENTE 1")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

    with col1:
        tipo1 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo1"
        )

    with col2:
        nombre1 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre1"
        )

    with col3:
        identificacion1 = st.text_input(
            "N° CC" if tipo1 == "Persona Natural" else "N° NIT",
            key="id1"
        )

    with col4:
        st.text_input("VALOR PROPUESTA 1", key="valor1")

    valor1, valor1_formateado = procesar_moneda("valor1")

    if valor1 > 0:
        st.write("Valor formateado:", valor1_formateado)
        st.success(valor_en_letras(valor1))

    representante1 = None
    cc_rep1 = None

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

    # =====================================================
    # PROPONENTE 2
    # =====================================================

    st.markdown("#### PROPONENTE 2")

    col5, col6, col7, col8 = st.columns([2, 2, 2, 3])

    with col5:
        tipo2 = st.selectbox(
            "TIPO PERSONA",
            ["Persona Natural", "Persona Jurídica"],
            key="tipo2"
        )

    with col6:
        nombre2 = st.text_input(
            "NOMBRE / RAZÓN SOCIAL",
            key="nombre2"
        )

    with col7:
        identificacion2 = st.text_input(
            "N° CC" if tipo2 == "Persona Natural" else "N° NIT",
            key="id2"
        )

    with col8:
        st.text_input("VALOR PROPUESTA 2", key="valor2")

    valor2, valor2_formateado = procesar_moneda("valor2")

    if valor2 > 0:
        st.write("Valor formateado:", valor2_formateado)
        st.success(valor_en_letras(valor2))

    representante2 = None
    cc_rep2 = None

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

    st.markdown("---")

 # =====================================================
# GUARDAR PLANEACIÓN
# =====================================================

st.markdown("---")

if st.button("GUARDAR PLANEACIÓN", use_container_width=True):

    if not proceso_existe(ID):
        st.error("Debe guardar primero el Estudio Previo.")

    else:
        conn = None

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Verificar si ya existe planeación para este proceso
            cursor.execute(
                "SELECT 1 FROM public.planeacion WHERE id_proceso = %s",
                (ID,)
            )

            existe_planeacion = cursor.fetchone()

            if existe_planeacion:
                st.warning("La planeación ya fue registrada para este proceso.")

            else:
                cursor.execute("""
                    INSERT INTO public.planeacion
                    (
                        id_proceso,
                        tipo1, nombre1, identificacion1, valor1,
                        representante1, cc_representante1,
                        tipo2, nombre2, identificacion2, valor2,
                        representante2, cc_representante2
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ID,
                    tipo1, nombre1, identificacion1, valor1,
                    representante1, cc_rep1,
                    tipo2, nombre2, identificacion2, valor2,
                    representante2, cc_rep2
                ))

                conn.commit()

                st.success("Planeación guardada correctamente.")

        except Exception as e:
            st.error(f"Error al guardar planeación: {e}")

        finally:
            if conn:
                conn.close()

# =====================================================
# ETAPA 3 — CONTRATACIÓN
# =====================================================

if etapa == "3 Contratación":

    st.markdown("### ETAPA 3 — CONTRATOS")

    tipo = st.selectbox(
        "TIPO CONTRATO",
        ["Obra", "Consultoría", "Prestación de Servicios", "Suministro"]
    )

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























