# 📦 SGI-U · Sistema de Gestión Inteligente de Inventario

> Dashboard interactivo de análisis predictivo y simulación temporal de inventario.  
> Proyecto universitario — Análisis Numérico aplicado a sistemas de gestión.


## 📌 Descripción

**SGI-U** es un sistema de simulación temporal de inventario que permite recorrer el tiempo día a día y observar cómo evolucionan las ventas, el stock y las alertas de reposición de una empresa de pastas artesanales.

El sistema pasa de ser **reactivo** (ver lo que ya pasó) a **predictivo** (anticipar quiebres de stock, detectar aumentos de demanda y proyectar el inventario futuro).

### Productos simulados

| Producto | Stock inicial | Punto de reposición |
|---|---|---|
| Sorrentinos Caseros | 320 u | 85 u |
| Ravioles de Verdura | 280 u | 65 u |
| Ñoquis Caseros | 350 u | 55 u |
| Canelones | 310 u | 40 u |

### Período simulado

`12/03/2026 → 15/07/2026` · 4 meses · ~90 días de datos por producto.

---

## ✨ Funcionalidades

- **Slider temporal**: recorrido día a día usando únicamente fechas reales del dataset
- **Estado inicial vacío**: el dashboard no muestra datos hasta que el usuario inicia la simulación
- **KPIs dinámicos**: Stock actual, Demanda promedio, Días restantes, Punto de reposición, Ingresos acumulados, % de quiebres — todos recalculados en tiempo real
- **Motor de alertas** con 4 reglas:
  - ⛔ Quiebre de stock o inminente
  - ⚠️ Stock bajo punto de reposición
  - 📈 Aumento de demanda detectado
  - 🔍 Predicción orientativa (pocos datos)
- **Predicción de ventas** con regresión lineal + proyección a 10 días
- **Stock proyectado** con zona crítica y día estimado de quiebre
- **Evolución histórica** del stock con marcas de reposición

---

## 🛠️ Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| Streamlit | ≥ 1.35 | Interfaz web interactiva |
| Pandas | ≥ 2.0 | Procesamiento de datos |
| Plotly | ≥ 5.20 | Gráficos interactivos |
| NumPy | ≥ 1.26 | Cálculos numéricos (regresión lineal) |

---

## 📁 Estructura del proyecto

```
simuladorinventario/
│
├── app.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias
├── README.md
│
├── components/
│   ├── alerts.py           # Motor de alertas (nativo Streamlit)
│   ├── charts.py           # Gráficos Plotly
│   └── kpis.py             # Cálculo y renderizado de KPIs
│
├── utils/
│   └── loader.py           # Carga de datos CSV
│
└── data/
    ├── ventas_dashboard.csv
    ├── inventario_dashboard.csv
    ├── indicadores.csv
    └── simulacion_stock.csv
```

---

## ⚙️ Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/victoriaefernandez311/simuladorinventario.git
cd simuladorinventario

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

El dashboard se abre en `http://localhost:8501`.

---

## ☁️ Despliegue en Streamlit Cloud

1. Repositorio **público** en GitHub ✓
2. Ingresá a [share.streamlit.io](https://share.streamlit.io)
3. Click en **"New app"**
4. Completá:
   - **Repository**: `victoriaefernandez311/simuladorinventario`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click en **"Deploy!"**

---

## 📊 Ciclo de simulación demostrable

Al mover el slider se puede observar el ciclo completo:

```
📦 Stock normal
    ↓
⚠️  Alerta de reposición (stock < punto mínimo)
    ↓
🔴  Riesgo de quiebre (menos de 7 días de stock)
    ↓
⛔  Quiebre de stock (stock = 0)
    ↓
📦  Reposición (triángulo naranja en el gráfico)
    ↓
✅  Recuperación del inventario
```

---

## 👩‍💻 Autores

| Nombre | Rol |
|---|---|
| Victoria E. Fernández | Desarrollo y análisis numérico |

> Proyecto universitario · Análisis Numérico · 2026