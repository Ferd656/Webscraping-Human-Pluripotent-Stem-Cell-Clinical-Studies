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

def extraer_detalles(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # variables alineadas con la creación de la DB
    datos = {
        "url": None,
        "estudio_clinico": None,
        "fase_estudio_clinico": None,
        "tipo_celula": None,
        "pais": None,
        "n_participantes": None,
        "fecha_inicio": None,
        "fecha_conclusion": None,
    }

    contenedor = soup.find("div", class_="l-box")
    if not contenedor:
        return None

    datos["url"] = url

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

def paso3_almacenar_data(urls, db_path, repositorio = "ensayos_PSC"):
    # Recibe la lista de urls y almacena la data en una base de datos y estructura dada
    if repositorio == "ensayos_PSC":
        for url in urls:
            data = extraer_detalles(url)
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
    paso3_almacenar_data(urls_paso2, db_path=DATABASE)

    # Finalización =====================================================================================================
    # solo activaremos esta opción si queremos que el webdriver termine. Para efectos de la
    # prac lo dejamos activado
    #driver.quit()

if __name__ == "__main__":
    main()



