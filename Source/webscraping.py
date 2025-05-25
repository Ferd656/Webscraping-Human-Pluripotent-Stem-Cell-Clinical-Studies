import re
import time
import requests
import base_de_datos
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Variables globales *********************************************

URL = "https://hpscreg.eu/browse/trials"
DATABASE = "../Dataset/ensayos_clinicos.db"

# ****************************************************************

def paso1_ordenar_elementos(driver):
    # Primera función, ordenaremos los casos clínicos de más recientes a más antiguos
    # para ello, usamos selenium.
    # Presionaremos el botón hasta que cambie la clase a 'ordenado'.
    buttons = WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located((By.TAG_NAME, "button"))
    )
    for btn in buttons:
        text = btn.text.strip()
        class_attr = btn.get_attribute("class")
        if text == "Start date" and "desc" not in class_attr:
            while "desc" not in class_attr:
                btn.click()
                time.sleep(1)
                class_attr = btn.get_attribute("class")
                #print(f"Botón presionado: '{text}' (clase: '{class_attr}')")
            return True
    return False

def paso2_obtener_datos(driver):
    #Obtiene los títulos y las rutas/referencias web para cada caso clínico
    titulos = []
    paginas = []

    # Espera a que se cargue el paginador
    WebDriverWait(driver, 10).until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.pagination li a'))
    )

    # Detectar número total de páginas (los botones numéricos del paginador)
    paginador = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination li a')
    numeros_paginas = [int(a.text) for a in paginador if a.text.isdigit()]
    total_paginas = max(numeros_paginas)

    for i in range(1, total_paginas + 1):
        WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'ol.list li div h3 a'))
        )

        a_elements = driver.find_elements(By.CSS_SELECTOR, 'ol.list li div h3 a')
        for a_element in a_elements:
            abbrs = a_element.find_elements(By.CSS_SELECTOR, 'abbr')
            titulos.append(abbrs[0].text.strip() if abbrs else "Sin título")
            paginas.append(a_element.get_attribute("href"))

        if i < total_paginas:
            next_page_button = driver.find_element(By.LINK_TEXT, str(i + 1))
            next_page_button.click()
            time.sleep(2)

    return paginas


# noinspection PyUnresolvedReferences,PyTypeChecker
def ictrp_url_info(ictrp_url, chrome_options, timeout=5):
    #Obtiene la data de ictrp
    options = chrome_options
    # Que no se nos abran las ventanas
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(ictrp_url)
    wait = WebDriverWait(driver, timeout)
    # Diccionario que contendrá las nuevas variables a recolectar:
    datos = {
        "edad_min": None,
        "edad_max": None,
        "genero": None,
        "tipo_estudio": None,
        "pais": None,
        "condiciones": None,
        "n_patrocinadores": None
    }
    # Subfunción para recopilar las variables:
    def get_text_by_id(id_, detalle=""):
        try:
            # Esperamos unos segundos a que cargue, especificado en el parámetro 'timeout'
            return wait.until(ec.presence_of_element_located((By.ID, id_)))
        except Exception as e:
            if detalle == "":
                msg = str(e)
            else:
                msg = "Sin data para para: " + detalle
            print(msg)
            return None
    # ----------------------------------------
    # Recopila la información de cada variable:
    edad_min = get_text_by_id("DataList6_ctl01_Label8", "edad mínima de los participantes")
    edad_max = get_text_by_id("DataList6_ctl01_Label11", "edad máxima de los participantes")
    genero = get_text_by_id("DataList6_ctl01_Label12", "género de los participantes")
    tipo_estudio = get_text_by_id("DataList3_ctl01_Study_typeLabel", "tipo de estudio")
    pais = get_text_by_id("DataList2_ctl01_Country_Label", "país")
    condiciones = get_text_by_id("DataList8_ctl01_Condition_FreeTextLabel", "condiciones de estudio")
    patrocinadores = get_text_by_id("DataList18", "patrocinadores")
    # ----------------------------------------
    # Almacena las variables en el diccionario:
    datos['edad_min'] = edad_min.text.strip() if edad_min is not None else None
    datos['edad_max'] = edad_max.text.strip() if edad_max is not None else None
    datos['genero'] = genero.text.strip() if genero is not None else None
    datos['tipo_estudio'] = tipo_estudio.text.strip() if tipo_estudio is not None else None
    datos['pais'] = pais.text.strip() if pais is not None else None
    if condiciones is not None:
        datos['condiciones'] = "|".join(
            line.strip() for
            line in
            condiciones.get_attribute("innerHTML").split("<br>") if
            line.strip()
        ).replace(";", "|")
        # Sin vacíos al final
        datos['condiciones'] = datos['condiciones'][:-1] if datos['condiciones'].endswith("|") else datos['condiciones']
    if patrocinadores is not None:
        rows = patrocinadores.find_elements(By.TAG_NAME, "tr")
        datos['n_patrocinadores'] = max(0, len(rows) - 1) #sin números negativos
    else:
        datos['n_patrocinadores'] = 0
    # ----------------------------------------
    # Finalizamos el driver para que no queden tropecientos objetos abiertos sin usar
    driver.quit()
    # ----------------------------------------
    # Devuelve el diccionario:
    return datos

# noinspection PyTypeChecker,PyUnresolvedReferences
def extraer_detalles(url, chrome_options):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # variables alineadas con la creación de la DB
    datos = {
        "url": None,
        "estudio_clinico": None,
        "tipo_estudio": None,
        "fase_estudio_clinico": None,
        "condicion_primaria_estudio": None,
        "condicion_secundaria_estudio": None,
        "tipo_celula": None,
        "pais": None,
        "n_participantes": None,
        "edad_min_participante": None,
        "edad_max_participante": None,
        "genero_participante": None,
        "n_patrocinadores": None,
        "fecha_inicio": None,
        "fecha_conclusion": None
    }
    contenedor = soup.find("div", class_="l-box")
    if not contenedor:
        return None

    datos["url"] = url

    try:
        ictrp_tag = contenedor.find(
            string="ICTRP weblink"
        )
        if ictrp_tag is None:
            print("No se encontró la referencia 'ICTRP'")
        else:
            ictrp_url = ictrp_tag.find_next("td").find("a")['href']
            print(ictrp_url)
            datos_ictrp = ictrp_url_info(ictrp_url, chrome_options)
            if datos_ictrp["condiciones"] is not None:
                datos["condicion_primaria_estudio"] = datos_ictrp["condiciones"].split("|")[0].strip()
                if len(datos_ictrp["condiciones"].split("|")) > 1:
                    datos["condicion_secundaria_estudio"] = datos_ictrp["condiciones"].split("|")[-1].strip()
            # utilizamos expresiones regulares para extraer únicamente los números
            edad_min = "".join(re.findall(r"\d", datos_ictrp["edad_min"]))
            edad_max = "".join(re.findall(r"\d", datos_ictrp["edad_max"]))
            datos["edad_min_participante"] = edad_min if edad_min else None
            datos["edad_max_participante"] = edad_max if edad_max else None
            # -----------------------------------------------------------------------
            datos["genero_participante"] = datos_ictrp["genero"]
            datos["pais"] = datos_ictrp["pais"]
            datos["tipo_estudio"] = datos_ictrp["tipo_estudio"]
            datos["n_patrocinadores"] = datos_ictrp["n_patrocinadores"]
    except Exception as e:
        print(str(e))
        pass

    try:
        datos["estudio_clinico"] = contenedor.find(class_="multi-line").get_text(strip=True)
    except AttributeError:
        pass

    try:
        datos["fase_estudio_clinico"] = contenedor.find(
            string="Clinical trials phase"
        ).find_next("td").get_text(strip=True)
    except AttributeError:
        pass

    try:
        datos["tipo_celula"] = contenedor.find(
            string="Which differentiated cell type is used"
        ).find_next("td").find(
            "table",class_="pure-table pure-table-striped model-table"
        ).find(string="Label").find_next("td").get_text(strip=True)
    except AttributeError:
        pass

    if datos["pais"] is None:
        try:
            datos["pais"] = contenedor.find(
                string="Public contact"
            ).find_next("td").find(
                "table",class_="pure-table pure-table-striped model-table"
            ).find(string="Country").find_next("td").get_text(strip=True)
        except AttributeError:
            pass

    try:
        n_participantes = contenedor.find(
            string="Estimated number of participants"
        ).find_next("td").get_text(strip=True)
        datos["n_participantes"] = int(n_participantes) if n_participantes.isdigit() else None
    except AttributeError:
        pass

    try:
        datos["fecha_inicio"] = contenedor.find(string="Start date (estimated)").find_next("td").get_text(strip=True)
    except AttributeError:
        pass

    try:
        datos["fecha_conclusion"] = contenedor.find(string="End date (estimated)").find_next("td").get_text(strip=True)
    except AttributeError:
        pass

    return datos

def paso3_almacenar_data(urls, db_path, chrome_options, repositorio = "ensayos_PSC"):
    # Recibe la lista de urls y almacena la data en una base de datos y estructura dada
    if repositorio == "ensayos_PSC":
        for url in urls:
            data = extraer_detalles(url, chrome_options)
            base_de_datos.agregar_registro_psc(data, db_path)
        print("Base de datos actualizada!")
    else:
        print(f"Falta definir un procedimiento para el repositorio '{repositorio}'.")

def main():
    # Configuración del Webdriver ======================================================================================
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(URL)

    # Ejecución del proceso webscraping ================================================================================
    paso1_ordenar_elementos(driver)
    urls_paso2 = paso2_obtener_datos(driver)
    driver.quit() # Cerramos el driver
    paso3_almacenar_data(urls_paso2, db_path=DATABASE, chrome_options=chrome_options)
    # Finalización =====================================================================================================
    print("Proceso finalizado!")

if __name__ == "__main__":
    main()
