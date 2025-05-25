import pandas as pd
import base_de_datos

conn = base_de_datos.sqlite3.connect("../Dataset/ensayos_clinicos.db")
df = pd.read_sql_query("SELECT * FROM ensayos_PSC", conn) # <--- df = Data para trabajar
conn.close()

df.info()

# +---------------------+
# | Limpieza de datos   |
# +---------------------+

# Describir gráficamente el estado original de los datos


# Apliar limpieza y transformaciones (incluye construir la variable objetivo, de ser necesario)



# Describir gráficamente el estado final de los datos


# +-------------------------+
# | Modelo no supervisado   |
# +-------------------------+
'''
    Idea: 
        k-means para agrupar la condición primaria de estudio (enfermedad) según 
        la edad promedio de los pacientes y duración promedio del estudio.
'''




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