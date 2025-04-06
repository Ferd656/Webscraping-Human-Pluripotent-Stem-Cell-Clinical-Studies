import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ordenar_elementos(driver):
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

def main():
    # Configuración del Webdriver ======================================================================================
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://hpscreg.eu/browse/trials")

    # Ejecución del proceso webscraping ================================================================================
    ordenar_elementos(driver)

    # Finalización =====================================================================================================
    # solo activaremos esta opción si queremos que el webdriver termine. Para efectos de la
    # prac lo dejamos activado
    #driver.quit()

if __name__ == "__main__":
    main()



