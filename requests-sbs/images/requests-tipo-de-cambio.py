import requests
from bs4 import BeautifulSoup
import pandas as pd 

url = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/resultados/PD04640PD/html'

# Extraemos lo que hay en la página y, como la respuesta es un html,
# Usamos BeautifulSoup para poder leerlo correctamente
respuesta = requests.get(url)
soup = BeautifulSoup(respuesta.text, 'html.parser')

# Usamos la función find_all para extraer la tabla
filas = soup.find_all('tr')

# Aquí crearé un par de listas para almacenar los valores
fechas = []
valores = []

# Recorro cada fila de la tabla Soup y los valores los guardo en las listas
for fila in filas:
    fecha = fila.find('td', class_='periodo')
    valor = fila.find('td', class_='dato')
    
    if fecha and valor:
        # Por si acaso, quitamos espacios en blanco
        fechas.append(fecha.text.strip())
        valores.append(valor.text.strip())

# Genero un diccionario para poder crear el dataframe
dict_tc = {
    'fecha':fechas,
    'tipo_de_cambio':valores
}

df = pd.DataFrame(dict_tc)

# Ahora, el problema es que las fechas las guarda con un formato 24Oct97, por lo que haré unas transformaciones adicionales
dict_mes = {
    'Ene':'-01-',
    'Feb':'-02-',
    'Mar':'-03-',
    'Abr':'-04-',
    'May':'-05-',
    'Jun':'-06-',
    'Jul':'-07-',
    'Ago':'-08-',
    'Set':'-09-',
    'Oct':'-10-',
    'Nov':'-11-',
    'Dic':'-12-'
}

# Reemplazar los meses por los valores del diccionario
for key, value in dict_mes.items():
    df['fecha'] = df['fecha'].str.replace(key, value)

# He detectado que en mi tabla hay duplicados, pero el importe es el mismo,
# Así que usaré Drop Duplicates sin perder datos adicionales
df = df.drop_duplicates(subset='fecha')

# Ahora que ya tengo mis fechas en un formato estandarizado. Ejm: 01-01-97, la convierto a datetime
df['fecha'] = pd.to_datetime(df['fecha'],format='%d-%m-%y')

# Para continuar, necesito establecer la columna fecha como índice
df.set_index('fecha', inplace=True)

# Ahora tengo un problema:
# No tengo todos los días debido a que solo se toman en cuenta los días hábiles, 
# sin embargo, me gustaría tener el rango completo de fechas, sean hábiles o no

# Aquí creamos un rango de fechas que cubra el rango completo de fechas del DataFrame por día
rango_fechas = pd.date_range(start=df.index.min(), # primer día
                             end=df.index.max(), # ultimo día
                             freq='D' # Frecuencia: Días
                             )

# Reindexamos nuestro dataframe original con este cambio de fechas
df_tc = df.reindex(rango_fechas)

# Por normativa, cuando no se publica el TC, se debe utilizar el del día inmediato anterior
# Por lo que ahora rellenamos los valores con el último valor conocido
df_tc['tipo_de_cambio'] = df_tc['tipo_de_cambio'].replace('n.d.',pd.NA).ffill()

# Al momento de reindexar, nuestra columna pierde el nombre, por lo que le volveremos a agregar "Fecha" como cabecera
df_tc.reset_index(inplace=True)
df_tc.rename(columns={'index': 'fecha'}, inplace=True)

# Ordenamos de manera descendente
df_tc = df_tc.sort_index(ascending=False)

print(df_tc.head())