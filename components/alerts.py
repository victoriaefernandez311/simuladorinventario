import streamlit as st
import pandas as pd


def mostrar_alertas(kpis: dict, ventas_filtradas=None):
    """
    Motor de alertas 100% nativo de Streamlit.
    Se muestra en la columna derecha del dashboard.
    Siempre visible, sin dependencia de JavaScript ni iframes.

    Alerta 1 — Stock < Punto de Reposición   → Reponer producto
    Alerta 2 — Días restantes < 7            → Riesgo de quiebre
    Alerta 3 — Demanda creciente             → Aumento de demanda
    Alerta 4 — Modelo poco preciso           → Revisar predicción
    """

    stock_actual     = kpis["stock_actual"]
    demanda_promedio = kpis["demanda_promedio"]
    dias_restantes   = kpis["dias_restantes"]
    punto_reposicion = kpis["punto_reposicion"]

    st.markdown("**🔔 Alertas**")

    alertas_activas = 0

    # ── Alerta 1: Stock bajo o en quiebre ────────────────────────────
    if stock_actual == 0:
        st.error(
            "**⛔ Quiebre de stock**\n\n"
            "No hay unidades disponibles. Las ventas están detenidas. "
            "Emitir orden de reposición de inmediato."
        )
        alertas_activas += 1
    elif stock_actual < punto_reposicion:
        st.warning(
            f"**⚠️ Reponer producto**\n\n"
            f"El stock actual ({stock_actual} u) está por debajo del nivel "
            f"mínimo recomendado ({int(punto_reposicion)} u). "
            f"Realizar pedido antes de que se agote."
        )
        alertas_activas += 1

    # ── Alerta 2: Quiebre proyectado ─────────────────────────────────
    if stock_actual > 0:
        if dias_restantes < 3:
            st.error(
                f"**⛔ Quiebre inminente**\n\n"
                f"Con la demanda actual el stock se agota en "
                f"**{dias_restantes:.1f} días**. "
                f"Reposición urgente."
            )
            alertas_activas += 1
        elif dias_restantes < 7:
            st.warning(
                f"**⚠️ Riesgo de quiebre**\n\n"
                f"El stock alcanza para **{dias_restantes:.1f} días** "
                f"según el ritmo de ventas actual. "
                f"Planificar reposición esta semana."
            )
            alertas_activas += 1

    # ── Alerta 3: Demanda creciente ───────────────────────────────────
    if ventas_filtradas is not None and len(ventas_filtradas) >= 6:
        n = len(ventas_filtradas)
        mitad = n // 2
        dem_primera = ventas_filtradas["cantidad"].iloc[:mitad].mean()
        dem_segunda = ventas_filtradas["cantidad"].iloc[mitad:].mean()
        if dem_segunda > dem_primera * 1.10:
            cambio_pct = (dem_segunda - dem_primera) / dem_primera * 100
            st.info(
                f"**📈 Demanda en alza**\n\n"
                f"Las ventas crecieron un **{cambio_pct:.0f}%** en el último "
                f"período ({dem_primera:.1f} → {dem_segunda:.1f} u/día). "
                f"Considere aumentar el stock de seguridad."
            )
            alertas_activas += 1

    # ── Alerta 4: Predicción poco fiable ─────────────────────────────
    # Se calcula internamente en charts; aquí lo determinamos con pocos datos
    if ventas_filtradas is not None and len(ventas_filtradas) < 10:
        st.warning(
            "**🔍 Predicción orientativa**\n\n"
            "Hay pocos registros de ventas en el período. "
            "El modelo explica parcialmente el comportamiento. "
            "Se recomienda avanzar el slider para obtener una proyección más confiable."
        )
        alertas_activas += 1

    # ── Sin alertas: estado saludable ────────────────────────────────
    if alertas_activas == 0:
        st.success(
            f"**✅ Inventario saludable**\n\n"
            f"Stock en niveles normales ({stock_actual} u), "
            f"demanda estable y sin riesgos detectados."
        )
