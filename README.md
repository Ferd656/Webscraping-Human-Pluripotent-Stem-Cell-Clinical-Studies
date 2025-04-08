
<img src="https://www.uoc.edu/content/experience-fragments/uoc-common/ww/en/site/mainfooter/master/_jcr_content/root/uocfooter/logoBlock/logo.coreimg.png/1730194024345/logo-uoc-negatiu.png"></img>

<h1>Webscraping: Human pluripotent stem cell clinical studies</h1>
<p><em>Máster en Ciencia de Datos - Tipología y ciclo de vida de los datos</em></p>

<h2>Desarrollado por:</h2>
<p>
▶️&nbsp;&nbsp;&nbsp;&nbsp;Ayoub Bentohami Amiah<br>
▶️&nbsp;&nbsp;&nbsp;&nbsp;Ferdinand Feoli Juárez
</p>

<h2>Estructura del repositorio:</h2>
<p>
📁&nbsp;&nbsp;&nbsp;&nbsp;Dataset<br>
&nbsp;├💽&nbsp;&nbsp;&nbsp;&nbsp;ensayos_clinicos.db <span style="font-size:10px; color: rgb(66, 135, 245);"><i>(archivo de base de datos SQLite que almacena la data recopilada de manera estructurada)</i></span><br>
&nbsp;└📄&nbsp;&nbsp;&nbsp;&nbsp;ensayos_PSC.csv <span style="font-size:10px; color: rgb(66, 135, 245);"><i>(archivo plano separador por tabulación que contiene la data correspondiente a la tabla 'ensayos_psc')</i></span><br>
📁&nbsp;&nbsp;&nbsp;&nbsp;Source<br>
&nbsp;├🤖&nbsp;&nbsp;&nbsp;&nbsp;base_de_datos.py  <span style="font-size:10px; color: rgb(66, 135, 245);"><i>(fichero python con funciones especializadas en la gestión de la base de datos)</i></span><br>
&nbsp;├🤖&nbsp;&nbsp;&nbsp;&nbsp;explorar.py  <span style="font-size:10px; color: rgb(66, 135, 245);"><i>(fichero python que ejecuta un análisis descriptivo sobre los datos)</i></span><br>
&nbsp;└🤖&nbsp;&nbsp;&nbsp;&nbsp;webscraping.py  <span style="font-size:10px; color: rgb(66, 135, 245);"><i>(fichero python con funciones para webscraping y limpieza de datos)</i></span><br>
</p>

<h2>Funcionamiento del programa:</h2>

<h3>▶️webscraping.py</h3>
<p>Este fichero contiene el código principal, se encarga de consultar la url objetivo y realiza las tareas necesarias de <i>webscraping</i> para obtener de esta la data necesaria. A continuación se describe las funciones que este fichero contiene:</p>

&nbsp;&nbsp;&nbsp;&nbsp;<b>• paso1_ordenar_elementos</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetro un objeto <i>webdriver</i> de la librería <i>Selenium</i>. Está específicamente diseñada para realizar un ordenamiento previo, de forma descendente, de los estudios publicados en la página respecto a su fecha de inicio. Para ello simula una acción de <i>click</i> a un elemento html específico el cual desencadena la función <i>javascript</i> que realiza dicha tarea.<br><br>
El propósito de esta función es asegurar que el programa escanee primero las publicaciones más recientes, descartando posteriormente aquellas que ya han sido almacenadas con anterioridad sin perder información, aumentando la eficiencia del escaneo.<br><br>
Esta es una función <i>void</i>, es decir, que no devuelve ningún valor.
</div><br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>• paso2_obtener_datos</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetro un objeto webdriver de la librería <i>Selenium</i>. Se encarga de recorrer las páginas de la url de manera ordenada y; a su vez, cada estudio publicado en cada una de estas páginas, recopilando la ruta url (subdominio) de cada estudio. Para ello, primero consulta el número total de páginas desde el elemento paginador, posteriormente realiza una iteración que recorre las <b>n</b> páginas encontradas, guardando en un objeto de lista las cadenas de texto de las url de cada estudio clínico publicado en cada página. <br><br>
Esta Función devuelve el objeto de lista con las url recopiladas.
</div><br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>• extraer_detalles</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetro una url y sirve como auxiliar de la función paso3_almacenar_data. Se encarga de extraer y transformar la data de un estudio clínico.<br><br>
Esta Función devuelve, en un objeto de diccionario, la data de interés ubicada en la url recibida como parámetro.
</div><br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>• paso3_almacenar_data</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetros una lista de urls como cadenas de texto, y como parámetros opcionales: la ruta de la base de datos y el nombre de la tabla en donde se almacenará la información.<br><br>
Se encarga de recorrer cada una de las urls recibidas como parámetro(obtenidas previamente de la función paso2_obtener_datos), para extraer la data de interés contenida en cada una (mediante la función extraer_detalles), y finalmente almacenar dicha data en la tabla y base de datos indicadas como parámetros mediante el llamado de una función invocada del fichero base_de_datos.py. Para ello, esta función utiliza las librerías <i>Requests</i> y <i>BeautifulSoup</i>.<br><br>
Esta es una función <i>void</i>, es decir, que no devuelve ningún valor.
</div><br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>• main</b><br>
<div style="margin-left: 40px;">Esta función no recibe parámetros, y se encarga de ejecutar los pasos de webscraping manera ordenada para capturar y almacenar la información.<br><br>
Primero, invoca un objeto <i>webdriver</i> de la librería <i>Selenium</i>, el cual navega al domino proporcionado por la variable global "URL". Luego ejecuta en orden las funciones: "paso1_ordenar_elementos", "paso2_obtener_datos" y "paso3_almacenar_data" pasando a las primeras dos el objeto webdriver como parámetro, y a la última le pasa las url devueltas por paso2_obtener_datos y la ruta de la base de datos contenida en la variable global "DATABASE".<br><br>
Esta es una función <i>void</i>, es decir, que no devuelve ningún valor.
</div><br>

<h3>▶️base_de_datos.py</h3>
<p>Este fichero contiene funciones específicas para la gestión y el almacenamiento de la data en la base de datos "ensayos_clinicos.db". Utiliza la librería SQLite. A continuación se describe las funciones que este fichero contiene:</p>

&nbsp;&nbsp;&nbsp;&nbsp;<b>• inicializar_repositorio</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetros opcionales la ruta de la base de datos y el nombre de la tabla en donde se almacenará la información.<br>Está diseñada para construir adecuadamente la tabla recibida como parámetro (si esta no existe previamente en la base de datos) siguiendo un esquema dado.<br><br>
Esta es una función <i>void</i>, es decir, que no devuelve ningún valor. 
</div><br>

&nbsp;&nbsp;&nbsp;&nbsp;<b>• agregar_registro_psc</b><br>
<div style="margin-left: 40px;">Esta función recibe como parámetros un objeto diccionario la ruta de la base de datos que contiene la tabla objetivo.<br>Está diseñada específicamente para insertar un registro a la tabla de ensayos clínicos llamada "ensayos_PSC", si el registro no existe previamente.<br><br>
Esta es una función <i>void</i>, es decir, que no devuelve ningún valor. 
</div><br>

<h3>▶️explorar.py</h3>
<p>Este fichero no contiene funciones. Está diseñado para que, al ser ejecutado, devuelva un breve resumen descriptivo de los datos almacenados en "ensayos_PSC", haciendo uso de las librerías <i>Pandas</i> y <i>SQLite</i>.</p>

<h3>▶️Modo de uso del programa</h3>

Para ejecutar el programa solamente se debe correr el <i>script</i> llamado webscraping.py, ya sea mediante el editor de código de preferencia o mediante el comando `python webscraping.py`.

<h2>Resultados:</h2>

Puede consultar un ejemplo de los datos resultantes tras una ejecución de este programa mediante el siguiente <a href="https://doi.org/10.5281/zenodo.15170761" target="_blank">enlace Zenodo</a>.
