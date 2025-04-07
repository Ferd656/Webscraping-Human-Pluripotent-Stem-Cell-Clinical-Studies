import pandas as pd
import base_de_datos

pd.set_option('display.max_columns', None)

conn = base_de_datos.sqlite3.connect("../Dataset/ensayos_clinicos.db")
df = pd.read_sql_query("SELECT * FROM ensayos_PSC", conn)
conn.close()

print(df.head())

print(df[["n_participantes"]].describe())