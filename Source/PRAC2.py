# ┏━━━━━━━━━━┓
# ┃ Módulos  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━┛
# Carga de módulos esenciales ------------------------------------------------------------------------------------------
import os
import sys
import math
import pandas as pd
import importlib.util
import seaborn as sns
from io import StringIO
import matplotlib.pyplot as plt
from scipy.stats import trim_mean
from sklearn.cluster import KMeans
from scipy.stats import normaltest
from sklearn.decomposition import PCA
from scipy.stats import chi2_contingency
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import r2_score, mean_squared_error, silhouette_score

# ┏━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Variables globales   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━┛
# Instancia variables globales -----------------------------------------------------------------------------------------
conn = None
numericas = None
categoricas = None
base_de_datos = None
rango_k = range(2, 13)
scaler = StandardScaler()

# ┏━━━━━━━━━━━━━┓
# ┃ Funciones   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━┛
# Instancia funciones --------------------------------------------------------------------------------------------------
def analisis_exploratorio(datos):
    global categoricas
    global numericas
    ## 1.2.1 Representación gráfica de completitud:
    sns.heatmap(datos.isnull(), cbar=False)
    plt.title("Gráfico de valores nulos(blancos) por variable")
    plt.show()
    ## 1.2.2 Distribución de variables numéricas
    i = 0
    n_cols = 2
    numericas = datos.select_dtypes(include=['int64', 'float64', 'Int64', 'Float64', 'datetime64', 'timedelta64'])
    n_vars = len(numericas.columns)
    n_rows = math.ceil(n_vars / n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
    axes = axes.flatten()
    for i, variable in enumerate(numericas.columns):
        sns.histplot(datos[variable].dropna(), kde=True, bins=30, ax=axes[i])
        axes[i].set_title(f"{variable}")
        axes[i].set_xlabel('')
        axes[i].set_ylabel('')
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    plt.show()
    ##  1.2.3 Cardinalidad y frecuencia de variables categóricas
    n_cols = 3
    categoricas = datos.select_dtypes(include=['object', 'category', 'bool', 'string'])
    n_vars = len(categoricas.columns)
    n_rows = math.ceil(n_vars / n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
    axes = axes.flatten()
    for i, variable in enumerate(categoricas.columns):
        datos[variable].value_counts(dropna=False).plot(kind='bar', ax=axes[i])
        axes[i].set_title(f"{variable}")
        axes[i].set_xlabel('')
        axes[i].set_ylabel('')
        if variable in ('tipo_celula', 'condicion_primaria_estudio', 'condicion_secundaria_estudio'):
            axes[i].set_xticklabels('')
        else:
            axes[i].set_xticklabels(list(datos[variable].unique()))
            axes[i].tick_params(axis='x', rotation=45)
        n_distinct = datos[variable].nunique(dropna=False)
        axes[i].text(
            0.95, 0.95,  # Position (relative to axes)
            f"Cardinalidad: {n_distinct}",
            transform=axes[i].transAxes,
            ha='right', va='top',
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", lw=1)
        )
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    plt.show()
def see_numerical_vars(_numericas, _df, _n_cols = 3):
    i = 0
    n_vars = len(_numericas.columns)
    n_rows = math.ceil(n_vars / _n_cols)
    fig, axes = plt.subplots(n_rows, _n_cols, figsize=(6 * _n_cols, 4 * n_rows))
    axes = axes.flatten()
    for i, variable in enumerate(_numericas.columns):
        if variable not in ['fecha_inicio', 'fecha_conclusion']:
            x = _df[[variable]].values
            y = _df["Target"].values
            model = LinearRegression()
            model.fit(x, y)
            y_pred = model.predict(x)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            sns.regplot(x=variable, y="Target", data=_df, scatter_kws={'alpha': 0.3}, ax=axes[i])
            axes[i].text(
                0.95, 0.95,
                f"$R^2$: {r2:.3f}\nMSE: {mse:.2f}",
                transform=axes[i].transAxes,
                ha='right', va='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", lw=1)
            )
            axes[i].set_title(f"{variable}")
            axes[i].set_xlabel('')
            axes[i].set_ylabel('')
    for j in range(i + (
            -1 if 'fecha_inicio' in _numericas.columns and
                  'fecha_conclusion' in _numericas.columns else
            1), len(axes)):
        fig.delaxes(axes[j])
    plt.show()
def see_categorical_vars(_categoricas, _df, _n_cols = 8):
    n_vars = len(_categoricas.columns)
    n_rows = math.ceil((n_vars*2) / _n_cols)
    fig, axes = plt.subplots(n_rows, _n_cols, figsize=(16, 4 * n_rows))
    axes = axes.reshape(n_rows, _n_cols)
    for i, variable in enumerate(_categoricas.columns):
        row = i % 2
        col = i - row
        sns.countplot(x=variable, data=_df, ax=axes[row, col])
        axes[row, col].set_title(f"{variable}")
        axes[row, col].set_xlabel('')
        axes[row, col].set_ylabel('')
        '''axes[row, col].tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)'''
        axes[row, col].tick_params(axis='x', rotation=45)
        sns.boxplot(x=variable, y="Target", data=_df, ax=axes[row, col+1])
        axes[row, col+1].set_xlabel('')
        axes[row, col+1].set_ylabel('')
        '''axes[row, col+1].tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)'''
        axes[row, col+1].tick_params(axis='x', rotation=45)
    plt.show()
def trim_mean_based_clustering(_df, var_name, _k, target_var ="Target", proportiontocut=0.05):
    means_df = (_df.groupby(var_name)[target_var].apply(
        lambda x: trim_mean(x, proportiontocut=proportiontocut)
    ).reset_index(name='mean_target'))
    kmeans = KMeans(n_clusters=_k, random_state=42)
    means_df[var_name + '_bin'] = kmeans.fit_predict(means_df[['mean_target']])
    return dict(
        silhouette=silhouette_score(means_df[['mean_target']], means_df[var_name + '_bin']),
        inertia=kmeans.inertia_,
        resultados=dict(zip(means_df[var_name], means_df[var_name + '_bin']))
    )
def buscar_k_optimo(_rango_k, var_name, _df):
    inertia = []
    silhouette = []
    max_elements = _df[var_name].nunique()
    ran = _rango_k if _rango_k.stop < max_elements else range(2,max_elements)
    for k in ran:
        # Objetivo: buscar el mayor valor de 'silhouette', donde la variación marginal de 'inertia' sea mínima
        objetocluster = trim_mean_based_clustering(_df, var_name, k)
        inertia.append(objetocluster['inertia'])
        silhouette.append(objetocluster['silhouette'])
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(ran,inertia, 'bo-', label='Inertia')
    ax2.plot(ran, silhouette, 'r^-', label='Silhouette')
    ax1.set_xlabel('Número de clústers (k)')
    ax1.set_ylabel('Inertia', color='blue')
    ax2.set_ylabel('Silhouette', color='red')
    plt.title(var_name)
    plt.show()
def bin_transform(_df, bins_obj):
    new_df = _df.copy()
    for col in bins_obj.keys():
        new_df.loc[:, col] = (
            new_df[col].map(bins_obj[col]['resultados']).fillna(new_df[col]).astype(str)
        )
    return new_df
def target_based_encoding(_df, target_column='Target'):
    df_encoded = _df.copy()
    diccionario = {}
    non_numeric_cols = _df.select_dtypes(include=['object', 'category', 'bool', 'string']).columns
    non_numeric_cols = [col for col in non_numeric_cols if col != target_column]
    for col in non_numeric_cols:
        target_means = df_encoded.groupby(col)[target_column].mean()
        diccionario[col] = target_means.to_dict()
        df_encoded[col] = df_encoded[col].map(target_means)
    return dict(diccionario = diccionario, df = df_encoded)

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Directorio de trabajo   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Validar que la base de datos exista en path --------------------------------------------------------------------------
ubicaciones = [
    ("./base_de_datos.py", "../Dataset/ensayos_clinicos.db"),
    ("./Source/base_de_datos.py", "./Dataset/ensayos_clinicos.db"),
    ("\\".join(sys.path[-1].split("\\")[:-1]) + "\\Source\\base_de_datos.py",
     "\\".join(sys.path[-1].split("\\")[:-1]) + "\\Dataset\\ensayos_clinicos.db")
]
for mdlpath in [i[0] for i in ubicaciones]:
    if os.path.exists(mdlpath):
        spec = importlib.util.spec_from_file_location("base_de_datos", mdlpath)
        base_de_datos = importlib.util.module_from_spec(spec)
        sys.modules["base_de_datos"] = base_de_datos
        spec.loader.exec_module(base_de_datos)
        break
if base_de_datos is None:
    print("Módulo de base de datos no encontrado. Revisar path.")
    print(sys.path)
    sys.exit(1)
for dbpath in [i[1] for i in ubicaciones]:
    if os.path.exists(dbpath):
        conn = base_de_datos.sqlite3.connect(dbpath)
        break
if conn is None:
    print("Base de datos no encontrada. Revisar path.")
    print(sys.path)
    sys.exit(1)
# ----------------------------------------------------------------------------------------------------------------------

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Recuperar conjunto de datos   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
df = pd.read_sql_query("SELECT * FROM ensayos_PSC", conn) # <--- Data para análisis
df = df.astype(base_de_datos.schema_to_pandas(conn)) # <--- Recuperamos del esquema los tipos de dato
conn.close()

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 1. Descripción del conjunto de datos   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# 1.1 Descripción general: dimensiones del conjunto de datos, tipos de dato y conteo de nulos --------------------------
buffer = StringIO()
df.info(buf=buffer)
print(
    """
+----------------------+
| Descripción general: |=====================================
+----------------------+
    """ +
    buffer.getvalue() +
"==========================================================="
)
# 1.2 Análsis exploratorio:  -------------------------------------------------------------------------------------------
'''
    Conociendo previamente la siguiente información:
       Las siguientes variables no aportan valor al análisis de patrones o predictivo:
       • "id": es una llave primaria auto-incremental
       • "url": son cadenas de texto con la dirección http del estudio clínico
       • "estudio_clinico": son cadenas de texto con los nombres de los estudios
    Se omite del dataset dichas variables, conservando el "id" como índice para eventual referencia.
'''
try:
    df.set_index('id', inplace=True) # <--- Conservamos el identificador como índice, para retroreferencia
    df.drop(['url', 'estudio_clinico'], axis=1, inplace=True)
except Exception as e:
    print(str(e))
    pass
analisis_exploratorio(df)

# ┏━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 2. Limpieza de datos   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━┛
# A raíz del análisis exploratorio se define la siguiente secuencia de tareas de limpieza:
df_clean = df.copy()
# 2.1 Tarea 1  ---------------------------------------------------------------------------------------------------------
'''
    Dado el problema que se quiere resolver. Eliminar registros que cumplan los siguientes criterio:
       - condicion_primaria_estudio = nulo y tipo_celula = nulo
       - n_participantes = nulo
'''
df_clean = df_clean[
    ~(df_clean['condicion_primaria_estudio'].isna() & df_clean['tipo_celula'].isna()) &
    df_clean['n_participantes'].notna()
]
# 2.2 Tarea 2  ---------------------------------------------------------------------------------------------------------
'''
    Imputar el valor "Desconocido" a los restantes nulos de las variables:
       - tipo_estudio
       - condicion_primaria_estudio
       - tipo_celula
       - pais
       - genero_participante
'''
df_clean[['tipo_estudio',
    'condicion_primaria_estudio',
    'tipo_celula',
    'pais',
    'genero_participante'
]] = df_clean[[
    'tipo_estudio',
    'condicion_primaria_estudio',
    'tipo_celula',
    'pais',
    'genero_participante'
]].fillna('Desconocido')
# 2.3 Tarea 3  ---------------------------------------------------------------------------------------------------------
'''
    Sabiendo previamente que los valores nulos de edad_min_participante y edad_max_participante
        no son errores, si no que representan la usencia de un límite de edad, imputar:
      - edad_min_participante = 0
      - edad_max_participante = 200
'''
df_clean[['edad_min_participante']] = df_clean[['edad_min_participante']].fillna(0)
df_clean[['edad_max_participante']] = df_clean[['edad_max_participante']].fillna(200)
# 2.4 Tarea 4  ---------------------------------------------------------------------------------------------------------
'''
    Transformación de las siguientes variables a booleano dada la alta concentración de uno de sus valores:
        - condicion_secundaria_estudio: Nulo = 0, el resto = 1
        - n_patrocinadores: Nulo o 0 = 0, el resto = 1
'''
df_clean['condicion_secundaria_estudio'] = df_clean['condicion_secundaria_estudio'].notna().astype(bool)
df_clean['n_patrocinadores'] = (
    ((df_clean['n_patrocinadores'].notna()) & (df_clean['n_patrocinadores'] != 0)).astype(bool))
# 2.5 Tarea 5  ---------------------------------------------------------------------------------------------------------
'''
    Tratamiento de los valores de las variables categóricas para darles consistencia en significado y formato
'''
## 2.5.1 Escaneo general
for colnm in categoricas:
    print(f"Variable '{colnm}':")
    print(df_clean[colnm].value_counts(dropna=False))
    print("-" * 40)
# #2.5.2 Variable: tipo_estudio
df_clean.loc[
    df_clean['tipo_estudio'].str.contains('interventional', case=False, na=False), 'tipo_estudio'
] ='Interventional'
df_clean.loc[
    df_clean['tipo_estudio'].str.contains('observational', case=False, na=False), 'tipo_estudio'
] = 'Observational'
## 2.5.2 Variable: fase_estudio_clinico
df_clean.loc[
    df_clean['fase_estudio_clinico'].str.contains('Phase 1', case=False, na=False), 'fase_estudio_clinico'
] = 'Phase 1'
df_clean.loc[
    df_clean['fase_estudio_clinico'].str.contains('Phase 2', case=False, na=False), 'fase_estudio_clinico'
] = 'Phase 2'
df_clean.loc[
    df_clean['fase_estudio_clinico'].str.contains('Alternative', case=False, na=False), 'fase_estudio_clinico'
] = 'Other'
## 2.5.3 Variable: condicion_primaria_estudio
mapeo_canonico = {
    # Parkinson
    "Parkinson Disease": "Parkinson's Disease",
    "PD - Parkinson's Disease": "Parkinson's Disease",
    "Parkinson's disease.": "Parkinson's Disease",
    "Early-onset Parkinson's Disease": "Parkinson's Disease",
    "Advanced Parkinson's Disease": "Parkinson's Disease",
    "Parkinson's disease": "Parkinson's Disease",
    # Macular Degeneration
    "Macular Degeneration": "Age-related Macular Degeneration",
    "Age Related Macular Degeneration": "Age-related Macular Degeneration",
    "Age-Related Macular Degeneration": "Age-related Macular Degeneration",
    "Dry Age-Related Macular Degeneration": "Age-related Macular Degeneration",
    "Dry Age Related Macular Degeneration": "Age-related Macular Degeneration",
    "Dry Macular Degeneration": "Age-related Macular Degeneration",
    "Dry Age-related Macular Degeneration": "Age-related Macular Degeneration",
    "Geographic Atrophy": "Age-related Macular Degeneration",
    "Neovascular age related macular degeneration": "Age-related Macular Degeneration",
    "Macular Degenerative Disease": "Age-related Macular Degeneration",
    "Macular degeneration diseases": "Age-related Macular Degeneration",
    # Graft vs Host Disease
    "Steroid-refractory Acute Graft-versus-host Disease(SR-aGVHD)": "Graft-vs-Host Disease",
    "Graft Versus Host Disease, Acute": "Graft-vs-Host Disease",
    "acute graft-versus-host disease": "Graft-vs-Host Disease",
    "Graft vs Host Disease": "Graft-vs-Host Disease",
    # Acute Myeloid Leukemia
    "Acute Myeloid Leukemia (AML)": "Acute Myeloid Leukemia",
    "AML, Adult": "Acute Myeloid Leukemia",
    # Stroke
    "Acute Ischemic Stroke": "Ischemic Stroke",
    "Stroke, Ischemic": "Ischemic Stroke",
    # Spinal Cord Injury
    "Spinal Cord Injury, Chronic": "Spinal Cord Injury",
    "spinal cord injury": "Spinal Cord Injury",
    "spinal cord injury at subacute stage": "Spinal Cord Injury",
    "Cervical Spinal Cord Injury": "Spinal Cord Injury",
    # Type 1 Diabetes
    "Type 1 Diabetes": "Type 1 Diabetes Mellitus",
    "Type 1 Diabetes Mellitus With Hypoglycemia": "Type 1 Diabetes Mellitus",
    # Dilated Cardiomyopathy
    "Dilated cardiomyopathy": "Dilated Cardiomyopathy",
    # Lymphoma, B-cell
    "B-cell Lymphoma": "B-cell Lymphoma",
    "Lymphoma, B-Cell": "B-cell Lymphoma",
    "Relapsed/Refractory B-Cell Lymphoma": "B-cell Lymphoma",
    # Non-Hodgkin Lymphoma
    "Indolent Non-Hodgkin Lymphoma": "Non-Hodgkin Lymphoma",
    # Meniscus Injury
    "meniscus injury": "Meniscus Injury",
    # Osteoarthritis
    "Articular cartilage damage, Articular cartilage disorder, Osteoarthritis": "Osteoarthritis",
    "Knee Osteoarthritis": "Osteoarthritis",
    "Musculoskeletal - Osteoarthritis": "Osteoarthritis",
    # COVID-19
    "Novel Coronavirus Pneumonia (COVID-19)": "COVID-19",
    #Vacío
    "": "Desconocido"
}
df_clean.loc[:, 'condicion_primaria_estudio'] = (
    df_clean['condicion_primaria_estudio'].map(mapeo_canonico).fillna(df_clean['condicion_primaria_estudio'])
)
## 2.5.4 Variable: tipo_celula
mapeo_canonico = {
    "Mesenchymal Stem Cell": "mesenchymal stem cell",
    "T cell": "cytotoxic T cell",
    "dendritic cell, human": "dendritic cell"
}
df_clean.loc[:, 'tipo_celula'] = (
    df_clean['tipo_celula'].map(mapeo_canonico).fillna(df_clean['tipo_celula'])
)
## 2.5.5 Variable: pais
df_clean.loc[
    df_clean['pais'].str.contains('China', case=False, na=False), 'pais'
] = 'China'
df_clean.loc[
    df_clean['pais'].str.contains('Korea', case=False, na=False), 'pais'
] = 'Korea'
df_clean.loc[
    df_clean['pais'].str.contains('Iran', case=False, na=False), 'pais'
] = 'Iran'
## 2.5.6 Variable: genero_participante
df_clean.loc[
    df_clean['genero_participante'].str.contains('Both', case=False, na=False), 'genero_participante'
] = 'All'
df_clean.loc[
    df_clean['genero_participante'].str.contains('and', case=False, na=False), 'genero_participante'
] = 'All'
df_clean.replace({'genero_participante':''}, "Desconocido", inplace=True)
# 2.6 Visualización del resultado  -------------------------------------------------------------------------------------
analisis_exploratorio(df_clean)
for colnm in categoricas:
    print(f"Variable '{colnm}':")
    print(df_clean[colnm].value_counts(dropna=False))
    print("-" * 40)

# ┏━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 3. Preprocesamiento   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━┛
# 3.1 Variable objetivo y partición del conjunto de datos  -------------------------------------------------------------
## 3.1.1 Construcción de la variable objetivo como la diferencia en días entre la fecha de inicio y
# fecha de conclusión del estudio
df_clean["Target"] = (df_clean["fecha_conclusion"] - df_clean["fecha_inicio"]).dt.days
## 3.1.2 Para modelar usamos únicamente los datos con registro empírico de fecha_conclusion
df_training = df_clean[(df_clean['Target'].notnull()) & (df_clean['fecha_conclusion'] < '2025-01-01')]
## 3.1.3 Un segundo subconjunto, que no tiene una fecha de conclusión definida, que podría ser utilizado
# como ejemplo de la aplicación del modelo para la estimación de la fecha
df_application = df_clean[df_clean['Target'].isnull()]
# 3.2 Visualizar las variables explicativas en función del objetivo  ----------------------------------------------------
## 3.2.1 Variables numércicas
see_numerical_vars(numericas, df_training)
## 3.2.2 Variables categóricas
see_categorical_vars(categoricas, df_training)
# 3.3 Ingeniería de características/variables  -------------------------------------------------------------------------
# Con base en la visualización anterior se define la siguiente secuencia de tareas:
'''
    Tarea 1: Crear nuevas variables numéricas a partir de n_participantes, edad_min_participante y 
             edad_max_participante.
             Evaluar su capacidad explicativa (Maximizar R² y minimizar MSE) respecto al target 
             para definir si conservar la(s) nueva(s) variable(s) o no.
'''
# Variable 1: Media edad de participación
df_training.loc[:, 'media_edad_participacion'] =(
        (df_training['edad_max_participante'] + df_training['edad_min_participante']) / 2)
# Variable 2: número de participantes al cuadrado
df_training.loc[:, 'n_participantes_2'] = df_training['n_participantes'] ** 2
# Variable 3: PCA
pca = PCA(n_components=1)
scaled_vars = scaler.fit_transform(
    df_training[['n_participantes', 'edad_min_participante', 'edad_max_participante']].dropna()
)
df_training.loc[:, 'participantes_PCA'] = pca.fit_transform(scaled_vars)
# Visualizar:
see_numerical_vars(
    df_training.loc[:,
        ['participantes_PCA', 'n_participantes_2', 'media_edad_participacion']
    ],
    df_training
)

'''
    Tarea 3: Agrupamiento de variables categóricas para valores de baja frecuencia
'''
# Variable 1: Condicion_primaria_estudio
buscar_k_optimo(rango_k, "condicion_primaria_estudio", df_training) # Resultado: 9
# Guardamos los objetos en un diccionario porque se van a necesitar luego para transformar los datos de testing
objetos_cluster = dict(
    condicion_primaria_estudio=trim_mean_based_clustering(df_training,"condicion_primaria_estudio",9)
)
# Variable 2: tipo_celula
buscar_k_optimo(rango_k, "tipo_celula", df_training) # Resultado: 5
objetos_cluster['tipo_celula'] = trim_mean_based_clustering(df_training,"tipo_celula",5)
# Variable 3: pais
buscar_k_optimo(rango_k, "pais", df_training) # Resultado: 6
objetos_cluster['pais'] = trim_mean_based_clustering(df_training,"pais",6)
# Variable 4: fase_estudio
objetos_cluster['fase_estudio_clinico'] = dict(
        silhouette=None,
        inertia=None,
        resultados={
            "Long term follow up": "Other",
            "Not applicable": "Other"
        }
    )
# Variable 5: genero_participante
objetos_cluster['genero_participante'] = dict(
        silhouette=None,
        inertia=None,
        resultados={
            "Female": "All",
            "Male": "All"
        }
    )

# 3.4 Selección de variables explicativas  -----------------------------------------------------------------------------
## 3.4.1 Selección preliminar
df_training_2 = df_training[[
    'edad_min_participante', # Se conserva al ser la variable con mayor R² y menor MSE (paso 3.3 tarea 1)
    'tipo_estudio',
    'condicion_primaria_estudio',
    'tipo_celula',
    'genero_participante',
    'fase_estudio_clinico',
    'pais',
    'n_patrocinadores',
    'Target'
]].copy()
## 3.4.2 Convertir las variables a numérico
### 3.4.2.1 Aplicar bins
df_training_2 = bin_transform(df_training_2, objetos_cluster)
see_categorical_vars(df_training_2.select_dtypes(include=['object', 'category', 'bool', 'string']), df_training_2)
### 3.4.2.2 Target-based encoding
df_training_diccionario = target_based_encoding(df_training_2)
df_training_2 = df_training_diccionario['df']
### 3.4.2.3 Visualización
see_numerical_vars(
    df_training_2[[
    'edad_min_participante',
    'tipo_estudio',
    'condicion_primaria_estudio',
    'tipo_celula',
    'genero_participante',
    'fase_estudio_clinico',
    'pais',
    'n_patrocinadores'
    ]],
    df_training_2
)
## 3.4.3 Análisis de multicolinealidad
corr_matrix = df_training_2.corr(numeric_only=True)
fig = plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0)
fig.show()
## 3.4.4 Selección final:
# Se descarta el género del participante al estar altamente correlacionada con la presencia de patrocinadores
df_training_final = df_training_2[[
    'edad_min_participante',
    'tipo_estudio',
    'condicion_primaria_estudio',
    'tipo_celula',
    'fase_estudio_clinico',
    'pais',
    'n_patrocinadores',
    'Target'
]].copy()
objetos_cluster.pop('genero_participante', None)

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 4. Modelo no supervisado   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
'''
    k-means para agrupar la condición primaria de estudio (enfermedad) según 
    la edad mínima promedio de los pacientes y duración promedio del estudio.
'''
kmeans_df = (
    df_training_final.groupby('condicion_primaria_estudio')[['edad_min_participante', 'Target']].mean().reset_index()
)
# Traducir los valores numércios de vuelta a su valor categórico -------------------------------------
translator = {v: k for k, v in df_training_diccionario['diccionario']['condicion_primaria_estudio'].items()}
kmeans_df.loc[:, 'condicion_primaria_estudio'] = (
    kmeans_df['condicion_primaria_estudio'].map(translator).astype(str)
)
#----------------------------------------------------------------------------------------------------
    # Variables para clustering
X = kmeans_df[['edad_min_participante', 'Target']]
X_scaled = scaler.fit_transform(X)
    # KMeans
kmeans = KMeans(n_clusters=3, random_state=0)
clusters = kmeans.fit_predict(X_scaled)
kmeans_df.loc[X.index, 'cluster'] = clusters
    # Visualización
plt.figure()
ax = sns.scatterplot(x='edad_min_participante', y='Target', hue='cluster', data=kmeans_df)
for i, row in kmeans_df.iterrows():
    ax.text(row['edad_min_participante'] + 0.1, row['Target'], row['condicion_primaria_estudio'], fontsize=9)
plt.title("Clustering por edad y duración")
plt.grid(True)
plt.show()
# Significado de cada categoría(punto en el gráfico):
for k, v in dict(
        sorted(objetos_cluster['condicion_primaria_estudio']['resultados'].items(), key=lambda item: item[1])
).items():
    print(str(k) +  " | " + str(v))

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 5. Modelo supervisado   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
'''
    Árbol regresor, para estimar una fecha aproximada de conclusión del estudo
    para aquellos que no tienen una fecha definida.
'''
# 5.1 Entrenamiento  ---------------------------------------------------------------------------------------------------
X = df_training_final.drop(columns='Target')
y = df_training_final['Target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
regressor = DecisionTreeRegressor(max_depth=5, random_state=42)
regressor.fit(X_train, y_train)
# 5.2 Testeo  ----------------------------------------------------------------------------------------------------------
y_pred = regressor.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R² Score: {r2}")
# 5.3 Visualización  ---------------------------------------------------------------------------------------------------
plt.figure()
plt.figure(figsize=(20, 10))
plot_tree(regressor, feature_names=X.columns, filled=True, rounded=True)
plt.show()


# ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ 6. Prueba de hpótesis   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
'''
    Idea: 
        H0 = La duración de un estudio es independiente de la edad promedio de los participantes
'''
# 6.1 Remover outliers -------------------------------------------------------------------------------------------------
# Habíamos puesto valor de 200 a los nulos de la edad, hay que revertir esa transformación
variables_contraste = dict(
    Target= df_training['Target'].dropna(),
    media_edad_participacion= df_training['media_edad_participacion'].dropna()
)
for var in variables_contraste.keys():
    data = variables_contraste[var]
    IQR_data = data[(data <= (data.quantile(0.95) if var =='Target' else 90 ))] # valores razonables de duración y edad
    plt.figure()
    sns.histplot(IQR_data, kde=True, bins=30)
    plt.show()
# 6.2 Prueba de normalidad de las variables ----------------------------------------------------------------------------
    stat, p = normaltest(IQR_data)
    print(f" Prueba de normalidad de D'Agostino-Pearson para '{var}': stat={stat:.4f}, p={p:.4f}")
    alpha = 0.05  # <-- punto crítico
    if p > alpha:
        print(f"✅ {var} es normal")
        variables_contraste[var] = IQR_data
    else:
        print(f"❌ {var} no es normal!")

# 6.3 Prueba chi-cuadrado ---------------------------------------------------------------------------------------------
contingencia = pd.crosstab(variables_contraste['Target'],variables_contraste['media_edad_participacion'])
chi2, p, dof, expected = chi2_contingency(contingencia)
print(f"Chi² = {chi2:.2f}, p = {p:.4f}")

if p < 0.05:
    print("Rechazamos H0: La duración del estudio depende de la edad de los participantes.")
else:
    print("No se puede rechazar H0: No hay evidencia de relación.")