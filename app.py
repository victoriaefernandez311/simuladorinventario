import streamlit as st
import pandas as pd

from utils.loader import (
    cargar_indicadores,
    cargar_ventas,
    cargar_inventario,
)

from components.kpis import (
    calcular_kpis_dinamicos,
    mostrar_kpis,
)

from components.alerts import mostrar_alertas

from components.charts import (
    mostrar_ventas_historicas,
    mostrar_prediccion_ventas,
    mostrar_stock_proyectado,
    mostrar_evolucion_stock,
)

# ══════════════════════════════════════════════
# CONFIGURACION DE PAGINA
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="SGI-U · Dashboard de Inventario",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; }
    hr { border-color: rgba(255,255,255,0.08) !important; }
    [data-testid="stMetricValue"] { font-size: 1.45rem !important; }

    /* Pantalla de inicio */
    .inicio-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;
        opacity: 0.85;
    }
    .inicio-icono { font-size: 64px; margin-bottom: 16px; }
    .inicio-titulo {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #e0e0e0;
    }
    .inicio-subtitulo {
        font-size: 1rem;
        color: #9e9e9e;
        max-width: 480px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════

@st.cache_data
def _cargar_datos():
    ventas     = cargar_ventas()
    inventario = cargar_inventario()
    config     = cargar_indicadores()
    return ventas, inventario, config


ventas, inventario, config_df = _cargar_datos()

fechas_disponibles = sorted(ventas["fecha"].dt.date.unique())

# ══════════════════════════════════════════════
# ENCABEZADO
# ══════════════════════════════════════════════

st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:2px; font-size:2rem;'>
        SGI-U &middot; Dashboard Inteligente de Inventario
    </h1>
    <p style='text-align:center; color:#9e9e9e; font-size:15px; margin-top:0;'>
        Sistema de Gestion de Inventario &middot; Simulacion Temporal Interactiva
    </p>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════
# PANEL DE CONTROL
# ══════════════════════════════════════════════

with st.container(border=True):

    col_ctrl_left, col_ctrl_right = st.columns([3, 1])

    with col_ctrl_left:
        st.markdown("#### Control de Simulacion Temporal")

        # El índice 0 es el estado "sin iniciar".
        # Los índices 1..N corresponden a fechas reales (fechas_disponibles[0..N-1]).
        indice_slider = st.slider(
            label="Arrastre para recorrer el tiempo",
            min_value=0,
            max_value=len(fechas_disponibles),
            value=0,
            step=1,
            format="Día %d",
            key="indice_fecha",
        )

        simulacion_iniciada = indice_slider > 0

        if simulacion_iniciada:
            fecha_actual_simulada = fechas_disponibles[indice_slider - 1]
            pct = (indice_slider) / len(fechas_disponibles) * 100
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; gap:18px; margin-top:4px;'>
                    <span style='font-size:22px; font-weight:700;'>
                        {fecha_actual_simulada.strftime('%d/%m/%Y')}
                    </span>
                    <span style='color:#9e9e9e; font-size:13px;'>
                        Dia {indice_slider} de {len(fechas_disponibles)}
                        &nbsp;&middot;&nbsp;
                        {pct:.0f}% del periodo
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style='margin-top:6px; color:#9e9e9e; font-size:14px;'>
                    ← Mueva el slider para iniciar la simulación
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_ctrl_right:
        st.markdown("#### Producto")
        productos_disponibles = config_df["producto"].tolist()
        producto = st.selectbox(
            "Seleccione producto",
            productos_disponibles,
            label_visibility="collapsed",
        )

# ══════════════════════════════════════════════
# ESTADO INICIAL — sin datos aún
# ══════════════════════════════════════════════

if not simulacion_iniciada:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="inicio-box">
            <div class="inicio-icono">💻</div>
            <div class="inicio-titulo">Inicio de Simulación</div>
            <div class="inicio-subtitulo">
                Seleccione una fecha moviendo el slider para comenzar la simulación.<br>
                Los indicadores, gráficos y alertas se activarán a medida que avance en el tiempo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ══════════════════════════════════════════════
# FILTRADO DE DATOS
# (solo se ejecuta cuando simulacion_iniciada = True)
# ══════════════════════════════════════════════

ventas_prod_full     = ventas[ventas["producto"] == producto]
inventario_prod_full = inventario[inventario["producto"] == producto]

ventas_filtradas = ventas_prod_full[
    ventas_prod_full["fecha"].dt.date <= fecha_actual_simulada
]

inventario_filtrado = inventario_prod_full[
    inventario_prod_full["fecha"].dt.date <= fecha_actual_simulada
]

# Periodo anterior para calcular delta en KPIs
n_dias_periodo = max(len(ventas_filtradas) // 2, 1)
ventas_previas = (
    ventas_filtradas.iloc[: -n_dias_periodo]
    if n_dias_periodo < len(ventas_filtradas)
    else ventas_filtradas.iloc[:0]
)
inventario_previo = (
    inventario_filtrado.iloc[: -n_dias_periodo]
    if n_dias_periodo < len(inventario_filtrado)
    else inventario_filtrado.iloc[:0]
)

config_producto = config_df[config_df["producto"] == producto].iloc[0]

# ══════════════════════════════════════════════
# KPIs DINÁMICOS
# ══════════════════════════════════════════════

st.divider()

kpis         = calcular_kpis_dinamicos(ventas_filtradas,  inventario_filtrado,  config_producto)
kpis_previos = calcular_kpis_dinamicos(ventas_previas,    inventario_previo,    config_producto)

mostrar_kpis(kpis, kpis_previos)

# ══════════════════════════════════════════════
# ALERTAS — columna derecha + panel principal
# ══════════════════════════════════════════════

st.divider()

col_graficos, col_alertas = st.columns([5, 1], gap="large")

with col_alertas:
    mostrar_alertas(kpis, ventas_filtradas)

# ══════════════════════════════════════════════
# GRAFICOS
# ══════════════════════════════════════════════

with col_graficos:
    col1, col2, col3 = st.columns([2, 3, 3], gap="large")

    with col1:
        st.subheader("Ventas Históricas")
        mostrar_ventas_historicas(ventas_filtradas)

    with col2:
        fig_pred, r2 = mostrar_prediccion_ventas(ventas_filtradas)
        st.subheader("Predicción de Ventas")
        # Interpretar r2 en lenguaje de negocio, sin mostrarlo
        if r2 >= 0.85:
            st.caption("Tendencia clara · Proyección a 10 días")
        elif r2 >= 0.5:
            st.caption("Tendencia aproximada · Revisar predicción")
        else:
            st.caption("Datos insuficientes · Predicción orientativa")
        st.plotly_chart(fig_pred, use_container_width=True)

    with col3:
        st.subheader("Stock Proyectado")
        mostrar_stock_proyectado(ventas_filtradas, inventario_filtrado, config_producto)

# ══════════════════════════════════════════════
# EVOLUCION HISTORICA DEL STOCK
# ══════════════════════════════════════════════

st.divider()

st.subheader("Evolución Histórica del Stock")
st.caption("Stock diario con marcas de reposición · Zona sombreada = zona crítica")
mostrar_evolucion_stock(inventario_filtrado, kpis["punto_reposicion"])
