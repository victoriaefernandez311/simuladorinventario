import streamlit as st


def calcular_kpis_dinamicos(ventas_filtradas, inventario_filtrado, config_producto):
    """
    Calcula KPIs dinámicamente a partir de los datos hasta la fecha simulada.
    
    Parámetros:
        ventas_filtradas    : DataFrame de ventas del producto hasta fecha_simulada
        inventario_filtrado : DataFrame de inventario del producto hasta fecha_simulada
        config_producto     : dict/Series con punto_reposicion, lead_time_dias, precio_unitario
    
    Retorna un dict con los KPIs calculados.
    """

    if inventario_filtrado.empty or ventas_filtradas.empty:
        return {
            "stock_actual":       0,
            "demanda_promedio":   0.0,
            "dias_restantes":     0.0,
            "punto_reposicion":   float(config_producto.get("punto_reposicion", 0)),
            "ingresos_periodo":   0.0,
            "tasa_quiebre":       0.0,
        }

    # Stock actual = stock_posterior de la última fila disponible
    stock_actual = int(inventario_filtrado.iloc[-1]["stock_posterior"])

    # Demanda promedio = media de cantidades vendidas en el período
    demanda_promedio = round(ventas_filtradas["cantidad"].mean(), 2)

    # Días restantes estimados
    dias_restantes = (
        round(stock_actual / demanda_promedio, 1)
        if demanda_promedio > 0 else 999.0
    )

    punto_reposicion = float(config_producto.get("punto_reposicion", 0))

    # Ingresos acumulados en el período
    ingresos_periodo = round(
        (ventas_filtradas["cantidad"] * ventas_filtradas["precio_unitario"]).sum(),
        0
    )

    # Tasa de quiebre: % días donde se vendió menos de lo disponible por falta de stock
    # Usamos inventario: días donde stock_anterior == 0 o stock_posterior == 0 tras demanda
    dias_con_quiebre = int((inventario_filtrado["stock_anterior"] == 0).sum())
    dias_totales = len(inventario_filtrado)
    tasa_quiebre = round(dias_con_quiebre / dias_totales * 100, 1) if dias_totales > 0 else 0.0

    return {
        "stock_actual":       stock_actual,
        "demanda_promedio":   demanda_promedio,
        "dias_restantes":     dias_restantes,
        "punto_reposicion":   punto_reposicion,
        "ingresos_periodo":   ingresos_periodo,
        "tasa_quiebre":       tasa_quiebre,
    }


def mostrar_kpis(kpis, kpis_previos=None):
    """
    Renderiza los KPIs con st.metric, incluyendo delta respecto al período anterior.
    
    kpis_previos: dict con los mismos campos, calculados un período antes.
    Permite mostrar el delta (▲/▼) en cada métrica.
    """

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    def _delta(key, fmt=None):
        if kpis_previos is None:
            return None
        d = kpis[key] - kpis_previos[key]
        if fmt:
            return fmt(d)
        return round(d, 2)

    with col1:
        st.metric(
            label="Stock Actual",
            value=f"{kpis['stock_actual']:,} u",
            delta=_delta("stock_actual", lambda d: f"{int(d):+,} u"),
            delta_color="normal"
        )

    with col2:
        st.metric(
            label="Demanda Promedio",
            value=f"{kpis['demanda_promedio']:.1f} u/día",
            delta=_delta("demanda_promedio", lambda d: f"{d:+.1f}"),
            delta_color="inverse"   # más demanda = advertencia
        )

    with col3:
        dias = kpis["dias_restantes"]
        color = "off" if dias >= 14 else "normal"
        st.metric(
            label="Días Restantes",
            value=f"{dias:.1f} días",
            delta=_delta("dias_restantes", lambda d: f"{d:+.1f} días"),
            delta_color=color
        )

    with col4:
        st.metric(
            label="Punto Reposición",
            value=f"{int(kpis['punto_reposicion'])} u",
        )

    with col5:
        ingresos = kpis["ingresos_periodo"]
        st.metric(
            label="Ingresos Período",
            value=f"${ingresos:,.0f}",
            delta=_delta("ingresos_periodo", lambda d: f"${d:+,.0f}"),
            delta_color="normal"
        )

    with col6:
        tasa = kpis["tasa_quiebre"]
        st.metric(
            label="Quiebres de Stock",
            value=f"{tasa:.1f}%",
            delta=_delta("tasa_quiebre", lambda d: f"{d:+.1f}%"),
            delta_color="inverse"  # más quiebres = peor
        )
