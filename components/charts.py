import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


# ──────────────────────────────────────────────
# Paleta compartida (dark theme)
# ──────────────────────────────────────────────
_TEMPLATE = "plotly_dark"
_COLOR_VENTAS   = "#4fc3f7"
_COLOR_PRED     = "#ff8a65"
_COLOR_STOCK    = "#81c784"
_COLOR_REPO     = "#ffb74d"
_COLOR_CRITICO  = "#ef5350"


def mostrar_ventas_historicas(ventas_filtradas: pd.DataFrame):
    """
    Gráfico de barras + línea de ventas diarias del producto.
    Eje X = fecha real (no id_venta).
    """

    if ventas_filtradas.empty:
        st.info("Sin datos para el período seleccionado.")
        return

    df = ventas_filtradas.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["fecha"],
        y=df["cantidad"],
        name="Ventas diarias",
        marker_color=_COLOR_VENTAS,
        opacity=0.75,
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Vendido: %{y} u<extra></extra>"
    ))

    # Media móvil 7 días
    if len(df) >= 7:
        df["mm7"] = df["cantidad"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["fecha"],
            y=df["mm7"],
            mode="lines",
            name="Media 7d",
            line=dict(color=_COLOR_PRED, width=2, dash="dot"),
            hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Media 7d: %{y:.1f} u<extra></extra>"
        ))

    fig.update_layout(
        template=_TEMPLATE,
        height=350,
        xaxis_title="Fecha",
        yaxis_title="Unidades Vendidas",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20),
        bargap=0.15,
    )

    st.plotly_chart(fig, use_container_width=True)


def mostrar_prediccion_ventas(ventas_filtradas: pd.DataFrame):
    """
    Regresión lineal sobre ventas del período.
    Retorna (fig, r2).
    """

    fig_vacio = go.Figure()
    fig_vacio.update_layout(
        template=_TEMPLATE, height=350,
        xaxis_title="Día", yaxis_title="Unidades Vendidas"
    )

    if len(ventas_filtradas) < 3:
        return fig_vacio, 0.0

    df = ventas_filtradas.copy().sort_values("fecha").reset_index(drop=True)
    x_num = np.arange(len(df))
    y = df["cantidad"].values

    pendiente, intercepto = np.polyfit(x_num, y, 1)
    y_pred = pendiente * x_num + intercepto

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    fechas = pd.to_datetime(df["fecha"])

    # Proyección 10 días hacia adelante
    n_proj = 10
    x_proj = np.arange(len(df), len(df) + n_proj)
    y_proj = pendiente * x_proj + intercepto
    ultimo_dia = fechas.iloc[-1]
    fechas_proj = [ultimo_dia + pd.Timedelta(days=i+1) for i in range(n_proj)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=fechas,
        y=y,
        mode="lines+markers",
        name="Ventas Reales",
        line=dict(color=_COLOR_VENTAS, width=2),
        marker=dict(size=5),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Real: %{y} u<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=fechas,
        y=y_pred,
        mode="lines",
        name="Tendencia (MRL)",
        line=dict(color=_COLOR_PRED, width=2, dash="dash"),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Tendencia: %{y:.1f} u<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=fechas_proj,
        y=y_proj,
        mode="lines+markers",
        name="Proyección (+10d)",
        line=dict(color=_COLOR_REPO, width=2, dash="dot"),
        marker=dict(size=4, symbol="diamond"),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Proyectado: %{y:.1f} u<extra></extra>"
    ))

    fig.update_layout(
        template=_TEMPLATE,
        height=350,
        xaxis_title="Fecha",
        yaxis_title="Unidades Vendidas",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20),
    )

    return fig, r2


def mostrar_stock_proyectado(ventas_filtradas: pd.DataFrame, inventario_filtrado: pd.DataFrame, config_producto):
    """
    Proyecta el stock futuro con demanda promedio calculada dinámicamente.
    Marca zona de peligro (punto de reposición) y el momento de quiebre.
    """

    punto_reposicion = float(config_producto.get("punto_reposicion", 0))

    if inventario_filtrado.empty or ventas_filtradas.empty:
        st.info("Sin datos suficientes para proyectar stock.")
        return

    stock_actual    = int(inventario_filtrado.iloc[-1]["stock_posterior"])
    demanda_promedio = ventas_filtradas["cantidad"].mean()

    if demanda_promedio <= 0:
        st.info("Demanda promedio es cero; no se puede proyectar.")
        return

    dias = np.arange(0, 21)
    stock_proy = stock_actual - demanda_promedio * dias
    stock_proy = np.clip(stock_proy, 0, None)

    # Día estimado de quiebre
    dia_quiebre = None
    for i, s in enumerate(stock_proy):
        if s <= 0:
            dia_quiebre = i
            break

    fig = go.Figure()

    # Zona de reposición (relleno rojo)
    fig.add_hrect(
        y0=0, y1=punto_reposicion,
        fillcolor="rgba(239,83,80,0.12)",
        line_width=0,
        annotation_text="Zona crítica",
        annotation_position="top left",
        annotation_font_size=11,
    )

    # Línea de punto de reposición
    fig.add_hline(
        y=punto_reposicion,
        line_dash="dash",
        line_color=_COLOR_REPO,
        annotation_text=f"Punto reposición ({int(punto_reposicion)} u)",
        annotation_position="bottom right",
        annotation_font_size=11,
    )

    # Stock proyectado
    fig.add_trace(go.Scatter(
        x=dias,
        y=stock_proy,
        mode="lines+markers",
        name="Stock Proyectado",
        line=dict(color=_COLOR_STOCK, width=3),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(129,199,132,0.1)",
        hovertemplate="Día +%{x}<br>Stock estimado: %{y:.0f} u<extra></extra>"
    ))

    # Marca de quiebre
    if dia_quiebre is not None:
        fig.add_vline(
            x=dia_quiebre,
            line_dash="dot",
            line_color=_COLOR_CRITICO,
            annotation_text=f"Quiebre día {dia_quiebre}",
            annotation_position="top right",
            annotation_font_color=_COLOR_CRITICO,
            annotation_font_size=12,
        )

    fig.update_layout(
        template=_TEMPLATE,
        height=350,
        xaxis_title="Días Futuros",
        yaxis_title="Stock (unidades)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=20, r=20, t=10, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


def mostrar_evolucion_stock(inventario_filtrado: pd.DataFrame, punto_reposicion: float):
    """
    Gráfico de evolución histórica del stock con reposiciones marcadas.
    Gráfico adicional opcional para mostrar en el dashboard.
    """

    if inventario_filtrado.empty:
        st.info("Sin datos de inventario.")
        return

    df = inventario_filtrado.copy().sort_values("fecha")
    fechas = pd.to_datetime(df["fecha"])

    fig = go.Figure()

    # Zona crítica
    fig.add_hrect(
        y0=0, y1=punto_reposicion,
        fillcolor="rgba(239,83,80,0.10)",
        line_width=0,
    )

    # Stock histórico
    fig.add_trace(go.Scatter(
        x=fechas,
        y=df["stock_posterior"],
        mode="lines",
        name="Stock",
        line=dict(color=_COLOR_STOCK, width=2),
        fill="tozeroy",
        fillcolor="rgba(129,199,132,0.08)",
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Stock: %{y} u<extra></extra>"
    ))

    # Marcas de reposición
    reposiciones = df[df["reposicion"] > 0]
    if not reposiciones.empty:
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(reposiciones["fecha"]),
            y=reposiciones["stock_posterior"],
            mode="markers",
            name="Reposición",
            marker=dict(
                symbol="triangle-up",
                size=12,
                color=_COLOR_REPO,
                line=dict(width=1, color="white")
            ),
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "Reposición: +%{customdata} u<extra></extra>"
            ),
            customdata=reposiciones["reposicion"].values
        ))

    fig.add_hline(
        y=punto_reposicion,
        line_dash="dash",
        line_color=_COLOR_REPO,
    )

    fig.update_layout(
        template=_TEMPLATE,
        height=300,
        xaxis_title="Fecha",
        yaxis_title="Stock (unidades)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=10, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)
