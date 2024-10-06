# Implementación de una BBDD Local en SQLite usando Python

Uno de los proyectos en los que he venido trabajando este año es el de hacer una medición de días del proceso de registro de facturas. La finalidad es poder identificar si estamos cumpliendo con los SLA e identificar posibles cuellos de botellas dentro del negocio

### Problemática

Para el momento que se me encomendó esta labor, no contaba con una base de datos estructurada con las tablas necesarias para poder sacar estos reportes a alto nivel. Es necesario hacer cruces bastante intensivos en rendimiento, por lo que herramientas como Power Query no iban a soportar la cantidad de datos de manera consistente.

## Desarrollo del Proyecto
### 1. Descarga SAP

Casi toda nuestra información está en nuestro ERP. No obstante, no es viable generar los reportes en archivos planos y transformarlos. Los sitios de Sharepoint tienen un límite de almacenamiento que, con la cantidad de datos disponibles, muy probablemente se nos haya quedar corto y no soy partidario de hacer conexiones a archivos planos de manera local.

Por el momento, estoy utilizando SQLite debido a la facilidad de uso. Además, para hacer los queries y probarlos, utilizo DB Browser for SQLite. Si bien ahora lo estamos manejando de manera local, eventualmente vamos a migrar esta información a un servidor. No obstante, cuando llegue ese momento, ya tendré los esquemas, los indices y tablas ya definidas.

Entonces, ¿cuál es la solución a este primer escenario?

- Realizar la descarga de los reportes de SAP: No tengo acceso a las tablas internas de SAP, así que lo tengo que manejar todo a nivel reporte
- Transformar cada uno de los datos y adecuarlos a un esquema SQL previamente definido.
- Cargar los Dataframes generados con Python a mi base de datos SQL
- A través de conexiones ODBC, utilizar esos datos para armar reportes en Power BI.

#### Input - Fecha

Primero, como input se le pide al usuario que ingrese el año y mes que se va a descargar en SAP, para que el script determine la fecha inicial (que es el primer día del mes) y el último (que va a depender del día). Con esto garantizamos que no se suba una fecha no válida, como una fecha futura o un caracter  no numérico.

![Fecha SAP](/etl-accounts-payable/images/fecha_sap.jpg)

#### Conexión SAP

Para poder conectarnos a SAP les paso un link donde explico más a detalle cómo hacer conexiones dinámicas a una sesión SAP: ![Manipulación de Sesiones y Conexiones SAP](https://github.com/alessandroperales74/apc-scripting/blob/main/Conexiones_SAP.md)

Una vez definida la sesión, hacemos el proceso de descarga. A continuación les muestro un script de descarga de la transacción FBL1H.

![Descarga SAP](/etl-accounts-payable/images/descarga_sap.jpg)

Así como este, tengo un script para cada transacción necesaria.

![Main SAP](/etl-accounts-payable/images/main.jpg)

### 2. Carga SQL

Para este paso, el script lee el archivo plano descargado previamente (puede ser un Excel o un txt) y lo transforma, adecuándolo al esquema definido en nuestra base de datos.

Es importante en este punto hacer un análisis previo sobre las columnas que vas a necesitas y qué tipo de dato tendrá cada columna. De eso dependerá la transformación que le haremos en Python.

Primero, establecemos la conexión con nuestra Base de Datos y, antes de ingresar los datos, para evitar duplicicidad de datos, le añadimos una sentencia SQL

```python
def validar_sql(nombre_tabla,cod_periodo):

    try:
        # Ejecutar la consulta SQL para eliminar registros del mismo periodo y evitar duplicidad
        cursor.execute(f"DELETE FROM {nombre_tabla} WHERE cod_periodo = '{cod_periodo}'")
    except:
        pass
```

A continuación, un ejemplo de cómo manejo mi conexión a la Base de Datos.

![Transformación SAP1](/etl-accounts-payable/images/sql_transformacion.jpg)

Finalmente, este es un ejemplo de una transformación de un archivo plano con Python.

![Transformación SAP2](/etl-accounts-payable/images/transformacion_sap.jpg)

#### Validar carga en la BBDD

Una vez que termino de correr todo el proceso, reviso si los datos están actualizados hasta el último periodo. A la fecha que subo esto, el último periodo fue setiembre 2024 (202409), así que puedo ver que mi base de datos está actualizado en el DB Browser.

![DB Browser](/etl-accounts-payable/images/db-browser.jpg)

Este es un ejemplo de un Query para validar el proceso de carga.

![Query SQL](/etl-accounts-payable/images/sql_query.jpg)

#### Optimización de la Base de Datos

Posteriormente ya me dedico a optimizar el rendimiento, como la creación de índices, vistas, etc.

![DB Browser 2](/etl-accounts-payable/images/db-browser2.jpg)

**Índices**

![DB Browser](/etl-accounts-payable/images/index_sql.jpg)

**Vistas**

![DB Browser](/etl-accounts-payable/images/views_sql.jpg)

### 3. Estructura del Proyecto

Aquí les muestro cómo he manejado la estructura de mi proyecto. Por un lado tengo los archivos en Python que importo como módulos y en otro lado tengo todos mis Queries de SQL.

![Estructura](/etl-accounts-payable/images/estructura_sql.jpg)

### 4. Power BI

Utilizando una conexión ODBC para Power BI, ingresamos el Query que extrae nuestra información necesaria el cual podemos ir probando en DB Browser. Si el resultado es correcto ahí, entonces debe funcionar en Power BI.

![ODBC Power BI](/etl-accounts-payable/images/odbc_powerbi.jpg)

Dicho query nos brinda la información necesaria para hacer la reportería necesaria. En este caso, estoy extrayendo información de las fechas de cada una de las etapas del proceso.

Como imaginarán, no puedo compartir los datos debido a que son confidenciales, pero les puedo mostrar el proceso que hago para actualizar este Dashboard, y el diseño que utilizamos para la medición de tiempos del proceso.

![Power BI 1](/etl-accounts-payable/images/power-bi.png)

Finalmente, podemos entrar a cada una de las etapas para ver el detalle por cada uno de los aspectos relevantes para el negocio.

![Power BI 2](/etl-accounts-payable/images/power-bi2.jpg)

### 5. Conclusiones

En resumen, las ventajas de esta implementación de una Base de Datos, sería lo siguiente:

- Actualmente, al contar con una Base de Datos reutilizable, tengo información unificada que puedo reutilizar en otros reportes.
- Además, el tiempo de descarga de información para la base de datos se hace en aproximadamente 45 minutos, cuando de manera manual podría tomarme medio día entero enfocado a esa labor, lo que significa una reducción significativa de FTEs.
- Al ya ser un proceso estandarizado, me aseguro de mantener un criterio único, transparente y bien documentado.
