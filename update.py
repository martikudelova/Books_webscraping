import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Načteme seznam knih z CSV
input_file = "moje_knihy.csv"  # Vstupní soubor
output_file = "moje_knihy_v2.csv"  # Výstupní soubor

# Spustíme Chrome
driver = webdriver.Chrome()

# Načteme knihy z CSV souboru do seznamu
books = []
with open(input_file, mode="r", encoding="utf-8-sig") as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Přeskočíme hlavičku
    for row in reader:
        books.append((row[0], row[1]))  # (název, autor)

output_data = []

# Procházíme knihy
for title, author in books:
    try:
        driver.get("https://www.databazeknih.cz/")
        
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "suggestMain"))
        )
        search_box.clear()
        search_box.send_keys(title)
        
        # Spouštíme hledání
        search_button = driver.find_element(By.CLASS_NAME, "mainSearchButton")
        driver.execute_script("arguments[0].click();", search_button)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "smallfind")))
        
        results = driver.find_elements(By.CLASS_NAME, "smallfind")
        found = False
        
        # Kontrola jmen
        for result in results:
            book_author = result.text.strip().split(",")[-1].strip()
            if book_author.lower() == author.lower():
                book_link = result.find_element(By.XPATH, "./preceding-sibling::a[1]")
                driver.execute_script("arguments[0].click();", book_link)
                found = True
                break
        
        if not found:
            print(f"⏩ {title} - autor nesouhlasí, přeskočeno.")
            continue
        
        # Čekáme na načtení dat
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[itemprop='datePublished']"))
        )
        
        # Získáme rok vydání
        year = driver.find_element(By.CSS_SELECTOR, "span[itemprop='datePublished']").text.strip()
        
        # Získáme počet stran
        more_info_button = driver.find_element(By.ID, "moreBookDetails")
        driver.execute_script("arguments[0].click();", more_info_button)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[itemprop='numberOfPages']"))
        )
        
        pages = driver.find_element(By.CSS_SELECTOR, "span[itemprop='numberOfPages']").text.strip()
        
        # Vložíme data do seznamu
        output_data.append([title, author, year, pages])
        print(f"✅ {title} - {year}, {pages} stran")
    
    except Exception as e:
        print(f"❌ Chyba u knihy {title}: {e}")
        continue

# Uložíme do CSV
with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Název", "Autor", "Rok vydání", "Počet stran"])
    writer.writerows(output_data)

print(f"✅ Hotovo! Data uložena do {output_file}")
driver.quit()