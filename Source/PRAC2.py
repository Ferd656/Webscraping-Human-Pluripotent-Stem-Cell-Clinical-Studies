import pandas as pd
import base_de_datos
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.stats import chi2_contingency


conn = base_de_datos.sqlite3.connect("../Dataset/ensayos_clinicos.db")
df = pd.read_sql_query("SELECT * FROM ensayos_PSC", conn) # <--- df = Data para trabajar
conn.close()

df.info()

# +---------------------+
# | Limpieza de datos   |
# +---------------------+

# Describir gráficamente el estado original de los datos

# Visualizar nulos
sns.heatmap(df.isnull(), cbar=False)
plt.title("Valores nulos por columna")
plt.show()

# Estadísticas generales
print(df.dtypes)

# Columna con muchos missings, si no es crítica, eliminarla
df.drop(columns=['condicion_secundaria_estudio', 'tipo_celula'], inplace=True)

    # Aplicar limpieza y transformaciones (incluye construir la variable objetivo, de ser necesario)

## Imputar edades faltantes con la mediana, el número de participantes con la media, sin patrocinadores si no se especifica, y
df['edad_min_participante'].fillna(df['edad_min_participante'].median(), inplace=True)
df['edad_max_participante'].fillna(df['edad_max_participante'].median(), inplace=True)
df['n_participantes'].fillna(df['n_participantes'].mean(), inplace=True)
df['genero_participante'].fillna('Desconocido', inplace=True)
df['n_patrocinadores'].fillna(0, inplace=True)

## Convertir fechas
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], errors='coerce')
df['fecha_final'] = pd.to_datetime(df['fecha_final'], errors='coerce')

## Duración del estudio en días
df['duracion_dias'] = (df['fecha_final'] - df['fecha_inicio']).dt.days

## Edad media del paciente (PROPUESTA)
df['edad_promedio'] = df[['edad_minima', 'edad_maxima']].mean(axis=1)

## Construir variable objetivo: estudio largo (>365 días) para knn NOTA: Cambiar para cualquier criterio de dias, ya sea +365 o cualquier otro valor
df['estudio_largo'] = df['duracion_dias'] > 365

    # Describir gráficamente el estado final de los datos

## Separar numéricas y categóricas
numericas = df.select_dtypes(include=['int64', 'float64'])
categoricas = df.select_dtypes(include=['object', 'category', 'bool'])

## 1. Distribución de variables numéricas
for col in numericas.columns:
    plt.figure(figsize=(6,4))
    sns.histplot(df[col].dropna(), kde=True, bins=30)
    plt.title(f"Distribución de {col}")
    plt.xlabel(col)
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()

## 2. Frecuencia de categorías
for col in categoricas.columns:
    plt.figure(figsize=(6,4))
    df[col].value_counts(dropna=False).plot(kind='bar')
    plt.title(f"Frecuencia de categorías - {col}")
    plt.xlabel(col)
    plt.ylabel("Conteo")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

## 3. Mapa de calor de correlaciones numéricas
if len(numericas.columns) > 1:
    plt.figure(figsize=(8,6))
    sns.heatmap(numericas.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlación entre variables numéricas")
    plt.tight_layout()
    plt.show()


# +-------------------------+
# | Modelo no supervisado   |
# +-------------------------+
'''
    Idea: 
        k-means para agrupar la condición primaria de estudio (enfermedad) según 
        la edad promedio de los pacientes y duración promedio del estudio.
'''
#   PROPUESTA DE CÓDIGO PARA EL ALGORTIMO
    # Variables para clustering
#X = df[['edad_promedio', 'duracion_dias']].dropna()
#scaler = StandardScaler()
#X_scaled = scaler.fit_transform(X)

    # KMeans
#kmeans = KMeans(n_clusters=3, random_state=0)
#clusters = kmeans.fit_predict(X_scaled)
#df.loc[X.index, 'cluster'] = clusters

    # Visualización
#sns.scatterplot(x='edad_promedio', y='duracion_dias', hue='cluster', data=df)
#plt.title("Clustering por edad y duración")
#plt.show()



# +-------------------------+
# | Modelo supervisado      |
# +-------------------------+

'''
    Idea 1: 
        Árbol regresor, para estimar una fecha aproximada de conclusión del estudo
        para aquellos que no tienen una fecha definida.
    Idea 2:
        Análisis discriminante para clasificar los estudios en "largo plazo" o "corto plazo".
'''






# +-------------------------+
# | Prueba de hipótesis     |
# +-------------------------+
'''
    Idea: 
        H0 = La duración de un estudio es independiente de la cantidad de patrocinadores
'''
#   PROPUESTA DE CÓDIGO PARA UNA PRUEBA CHI DE INDEPENDENCIA DE MUESTRAS!!!

    # Agrupar duración por número de patrocinadores
#df['num_patrocinadores'] = df['patrocinadores'].apply(lambda x: len(str(x).split(',')) if pd.notnull(x) else 0)
#df['categoria_duracion'] = pd.cut(df['duracion_dias'], bins=[0, 180, 365, 10000], labels=['corta', 'media', 'larga'])

    # Tabla de contingencia
#contingencia = pd.crosstab(df['num_patrocinadores'], df['categoria_duracion'])

    # Prueba chi-cuadrado
#chi2, p, dof, expected = chi2_contingency(contingencia)
#print(f"Chi² = {chi2:.2f}, p = {p:.4f}")

#if p < 0.05:
#    print("Rechazamos H0: La duración del estudio depende del número de patrocinadores.")
#else:
#    print("No se puede rechazar H0: No hay evidencia de relación.")