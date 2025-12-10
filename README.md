# Tesis: Prevención de Siniestros de Tránsito en Perú (2008-2023)

Este proyecto forma parte de la tesis para la **Prevención de Siniestros de Tránsito**, enfocada en la normalización, análisis y predicción de accidentes en Perú utilizando datos históricos desde 2008 hasta 2023.

El sistema integra un pipeline de datos robusto, análisis exploratorio avanzado con PySpark y una aplicación web interactiva para la predicción de siniestros basada en modelos de Machine Learning.

## 🚀 Características Principales

* **Pipeline ETL (Extract, Transform, Load):**
  * Normalización de datos crudos (Excel) a formatos optimizados (Parquet/CSV).
  * Limpieza y estandarización de nombres de regiones, fechas y categorías.
* **Análisis de Big Data con PySpark:**
  * Procesamiento eficiente de grandes volúmenes de datos.
  * Ingeniería de características (lags, tendencias, índices de fin de semana/noche).
* **Modelado Predictivo:**
  * **Random Forest Regressor:** Modelo robusto que captura interacciones complejas entre regiones y factores temporales.
  * Ingeniería de características avanzada con codificación de regiones (OneHotEncoder).
* **Aplicación Web Interactiva:**
  * Interfaz amigable para realizar predicciones en tiempo real por región, fecha y condiciones climáticas.
  * Disponible en versión Web (Flask) y Standalone (HTML).

## 📂 Estructura del Proyecto

```text
tesis-prevencion-siniestros-transito/
├── data/                   # Datos crudos y procesados (no incluidos en el repo)
├── notebooks/              # Jupyter Notebooks para análisis y ML
│   ├── normalizacion_nb.ipynb  # Limpieza y generación de tablas Gold/Silver
│   ├── prediction_nb.ipynb     # Entrenamiento del modelo y evaluación
│   ├── prediction_app.py       # Aplicación Web (Flask)
│   └── prediction_standalone.html # Interfaz de predicción offline
├── scripts/                # Scripts de utilidad (normalización, pivoteo, verificación)
│   ├── normalizar_siniestros.py
│   ├── pivot_wide.py
│   └── verify_outputs.py
├── src/                    # Código fuente del paquete Python
│   └── tesis_prevencion_siniestros_transito/
│       └── normalize.py    # Lógica de normalización ETL
├── tests/                  # Pruebas unitarias
├── reports/                # Reportes de calidad de datos
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
```

## 🛠️ Instalación

1. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/<tu-usuario>/tesis-prevencion-siniestros-transito.git
    cd tesis-prevencion-siniestros-transito
    ```

2. **Crear y activar un entorno virtual:**

    ```bash
    python -m venv .venv
    # Mac/Linux
    source .venv/bin/activate
    # Windows
    # .\.venv\Scripts\Activate.ps1
    ```

3. **Instalar dependencias:**

    ```bash
    pip install -U pip
    pip install -r requirements.txt
    pip install -e .
    ```

## 📖 Uso

### 1. Normalización de Datos (ETL)

Para procesar el archivo Excel original y generar los datasets limpios:

```bash
tpst-normalizar "data/raw/PERU. SINIESTROS DE TRANSITO POR AÑO 2008-2023.xlsx" \
    -o "data/processed/siniestros_normalizado.csv" \
    --parquet "data/processed/siniestros_normalizado.parquet" \
    --verify
```

### 2. Análisis y Entrenamiento (Notebooks)

* Ejecuta `notebooks/normalizacion_nb.ipynb` para realizar la limpieza profunda y generar las tablas analíticas (Silver/Gold).
* Ejecuta `notebooks/prediction_nb.ipynb` para entrenar el modelo predictivo y evaluar su desempeño.

### 3. Aplicación de Predicción

Para iniciar la interfaz web y realizar predicciones:

**Opción A: Servidor Flask (Recomendado)**

```bash
python notebooks/prediction_app.py
```

Luego abre `http://localhost:5000` en tu navegador.

**Opción B: Versión Standalone**
Simplemente abre el archivo `notebooks/prediction_standalone.html` en cualquier navegador web.

### 4. Dashboard de Resultados

Para visualizar el rendimiento del modelo y las proyecciones futuras:

1. **Generar datos del dashboard:**
    Asegúrate de haber ejecutado el notebook de predicción (`prediction_nb.ipynb`) para generar los modelos. Luego ejecuta:

    ```bash
    python notebooks/prepare_dashboard_data.py
    ```

    Esto creará el archivo `dashboard_data.json`.

2. **Visualizar:**
    Abre el archivo `notebooks/dashboard.html` en tu navegador web para ver:
    * Comparativa de valores reales vs. predichos.
    * Métricas de error (MAPE, RMSE).
    * Proyecciones para 2024-2025.

### 5. Dashboard Optimizado (Recomendado)

Para una experiencia visual mejorada con gráficos interactivos y métricas detalladas:

1. Asegúrate de haber generado los datos (`dashboard_data.json`) como se indica en el paso anterior.
2. Abre el archivo `notebooks/dashboard_enhanced.html` en tu navegador.
    * Incluye gráficos interactivos con **Plotly**.
    * Tablas de estado con semáforos de precisión.
    * Líneas de tiempo comparativas por región.

### 6. Despliegue Local de Dashboards (Importante)

Para que los dashboards (`dashboard.html` y `dashboard_enhanced.html`) funcionen correctamente y puedan cargar los datos JSON, **es necesario ejecutarlos a través de un servidor web local** (debido a políticas de seguridad CORS de los navegadores).

No te preocupes, Python incluye uno por defecto. Sigue estos pasos:

1. Abre una terminal en la carpeta raíz del proyecto.
2. Ejecuta el siguiente comando para iniciar un servidor simple:

    ```bash
    python -m http.server 8000
    ```

3. Abre tu navegador y ve a las siguientes direcciones:
    * **Dashboard Básico:** [http://localhost:8000/notebooks/dashboard.html](http://localhost:8000/notebooks/dashboard.html)
    * **Dashboard Optimizado:** [http://localhost:8000/notebooks/dashboard_enhanced.html](http://localhost:8000/notebooks/dashboard_enhanced.html)
    * **Predicción Standalone:** [http://localhost:8000/notebooks/prediction_standalone.html](http://localhost:8000/notebooks/prediction_standalone.html)

> **Nota:** Si solo abres los archivos con doble clic (file://...), es posible que no carguen los datos correctamente.

## 📊 Calidad de Datos

El proyecto incluye verificaciones automáticas de calidad de datos. Los reportes se generan en `reports/data_quality_report.json` tras ejecutar los notebooks de procesamiento.

## 📄 Licencia

Este proyecto es parte de una investigación académica.
