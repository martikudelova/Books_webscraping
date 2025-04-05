import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Cesty k souborům
VSTUPNI_SOUBOR = "autori.csv"  # CSV se seznamem autorů (1 sloupec - jména autorů)
VYSTUPNI_SOUBOR = "autori_s_narodnosti.csv"  # CSV s přidanými národnostmi

# Inicializace Selenium WebDriver
driver = webdriver.Chrome()

try:
    # Otevřeme stránku
    driver.get("https://www.cbdb.cz/stream")
    driver.maximize_window()

    # Načteme seznam autorů z CSV
    with open(VSTUPNI_SOUBOR, "r", encoding="utf-8") as f:
        cteni = csv.reader(f, delimiter=";")
        autori = [radek[0] for radek in cteni]  # Čteme první sloupec (jména autorů)

    vysledky = []  # Sem budeme ukládat výsledky

    for autor in autori:
        try:
            print(f"🔍 Hledám autora: {autor}")

            # Najdeme vyhledávací pole a zadáme jméno autora
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search_text")))
            search_box.clear()  # Vyčistit pole před novým hledáním
            search_box.send_keys(autor)

            # Klikneme na tlačítko hledání (lupa)
            search_button = driver.find_element(By.CLASS_NAME, "search_button")
            search_button.click()

            # Počkáme na načtení výsledků
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "short_subitem_authors")))

            # Ujistíme se, že hledáme autora a ne knihu - klikneme na sekci "Autoři"
            authors_tab = driver.find_element(By.ID, "short_subitem_authors")
            authors_tab.click()

            # Počkáme, až se zobrazí výsledky
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search_graphic_box_img")))

            # Klikneme na prvního nalezeného autora
            first_author = driver.find_element(By.CSS_SELECTOR, ".search_graphic_box_img")
            driver.execute_script("arguments[0].click();", first_author)

            # Počkáme, než se načte stránka autora
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

            # Najdeme prvek s národností
            try:
                birthplace = driver.find_element(By.XPATH, '//span[@itemprop="birthPlace"]').text.strip()
            except:
                birthplace = "Neznámá národnost"

            print(f"🌍 {autor} - Národnost: {birthplace}")

            # Uložíme výsledek
            vysledky.append([autor, birthplace])

        except Exception as e:
            print(f"⚠️ Chyba u autora {autor}: {e}")
            vysledky.append([autor, "Chyba při hledání"])

        # Po každém hledání chvíli počkáme, aby stránka neměla problém s přetížením
        time.sleep(2)

    # Uložíme do CSV
    with open(VYSTUPNI_SOUBOR, "w", encoding="utf-8-sig", newline="") as f:
        zapis = csv.writer(f, delimiter=";")
        zapis.writerow(["Autor", "Národnost"])
        zapis.writerows(vysledky)

    print(f"✅ Hotovo! Výsledky uloženy do '{VYSTUPNI_SOUBOR}'.")

finally:
    driver.quit()  # Zavřeme prohlížeč