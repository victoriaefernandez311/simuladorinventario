import pandas as pd


def cargar_indicadores():
    return pd.read_csv("data/indicadores.csv")


def cargar_ventas():
    df = pd.read_csv("data/ventas_dashboard.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def cargar_inventario():
    df = pd.read_csv("data/inventario_dashboard.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def cargar_alertas():
    return pd.read_csv("data/alertas.csv")


def cargar_simulacion():
    return pd.read_csv("data/simulacion_stock.csv")
