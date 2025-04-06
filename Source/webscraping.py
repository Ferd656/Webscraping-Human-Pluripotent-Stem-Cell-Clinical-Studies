import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def paso1_ordenar_elementos(driver):
    # Primera función, ordenaremos los casos clínicos de más recientes a más antiguos
    # para ello, usamos selenium.
    # Presionaremos el botón hasta que cambie la clase a 'ordenado'.
    buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
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
    a_elements = driver.find_elements(By.CSS_SELECTOR, 'ol.list li div h3 a')

    for a_element in a_elements:
        titulos.append(a_element.find_elements(By.CSS_SELECTOR, 'abbr')[0].text.strip())
        print(a_element.find_elements(By.CSS_SELECTOR, 'abbr')[0].text.strip())
        paginas.append(a_element.get_attribute("href"))
        print(a_element.get_attribute("href"))

    return paginas

def paso3_extraer_detalles(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # variables alineadas con la creación de la DB
    datos = {
        "estado_clinico": None,
        "tipo_celula": None,
        "n_participantes": None,
        "fecha_inicio": None,
        "fecha_conclusion": None,
    }

    contenedor = soup.find("div", class_="l-box")
    if not contenedor:
        return None

    try:
        estado_clinico = contenedor.find(string="Clinical status").find_next("td").get_text(strip=True)
        datos["estado_clinico"] = estado_clinico
    except AttributeError:
        pass

    try:
        tipo_celula = contenedor.find(string="Which differentiated cell type is used").find_next("td").find("table", class_="pure-table pure-table-striped model-table").find(string="Label").find_next("td").get_text(strip=True)
        datos["tipo_celula"] = tipo_celula
    except AttributeError:
        pass

    try:
        n_participantes = contenedor.find(string="Estimated number of participants").find_next("td").get_text(strip=True)
        datos["n_participantes"] = int(n_participantes) if n_participantes.isdigit() else None
    except AttributeError:
        pass

    try:
        fecha_inicio = contenedor.find(string="Start date (estimated)").find_next("td").get_text(strip=True)
        datos["fecha_inicio"] = fecha_inicio
    except AttributeError:
        pass

    try:
        fecha_conclusion = contenedor.find(string="End date (estimated)").find_next("td").get_text(strip=True)
        datos["fecha_conclusion"] = fecha_conclusion
    except AttributeError:
        pass

    return datos



def main():
    # Configuración del Webdriver ======================================================================================
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://hpscreg.eu/browse/trials")

    # Ejecución del proceso webscraping ================================================================================
    paso1_ordenar_elementos(driver)
    paso2_obtener_datos(driver)

    # Finalización =====================================================================================================
    # solo activaremos esta opción si queremos que el webdriver termine. Para efectos de la
    # prac lo dejamos activado
    #driver.quit()

if __name__ == "__main__":
    main()



