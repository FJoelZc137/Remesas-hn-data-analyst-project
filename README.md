# 📊 Proyecto de Análisis de Remesas en Honduras

Este repositorio contiene un proyecto de **ETL + Análisis de Datos + Visualización** sobre las remesas que ingresan a Honduras.  
El objetivo es transformar los datos, generar métricas relevantes y crear gráficos que permitan entender mejor la evolución de las remesas.

---

##  Objetivos del proyecto
- Analizar la evolución histórica de las remesas en Honduras.
- Calcular métricas clave: crecimiento anual, máximos, mínimos y medias móviles.
- Visualizar los datos de forma clara con Python (pandas, matplotlib, seaborn, Power BI).
- Sentar bases para futuros tableros interactivos y reportes más avanzados.

---

## 📂 Estructura del proyecto

remesas-hn/
│
├── data/
│ ├── raw/ # Datos en bruto (fuente original, SECMCA / BCH)
│ ├── processed/ # Datos procesados (limpios y listos para análisis)
│
├── notebooks/ # Jupyter notebooks con análisis exploratorio
├── scripts/ # Scripts de Python para ETL y métricas
│ ├── clean_secmca.py
│
├── README.md # Documentación del proyecto
└── requirements.txt # Librerías necesarias


---

## 🛠️ Tecnologías utilizadas
- **Python 3.13+**
- Librerías:
  - `pandas` → Limpieza y transformación de datos
  - `matplotlib` / `seaborn` → Visualizaciones
  - `openpyxl` → Manejo de Excel
- **Git & GitHub** → Control de versiones y colaboración
- **Power BI (opcional)** → Dashboards dinámicos

---

⚙️ Instalación y uso

Clonar el repositorio:

git clone https://github.com/FJoelZc137/Remesas-hn-data-analyst-project.git
cd Remesas-hn-data-analyst-project


Crear un entorno virtual:

python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows


Instalar dependencias:

pip install -r requirements.txt


Ejecutar scripts o notebooks:

python scripts/clean_secmca.py


## 👨‍💻 Autor
**Fredy Joel Zelaya** – Data Analyst 

