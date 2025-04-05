import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Přihlašovací údaje
USERNAME = "username" # Doplň uživatelské jméno
PASSWORD = "password" # Doplň heslo

# Načteme seznam knih
csv_file = "moje_knihy.csv"
books = {}

with open(csv_file, mode="r", encoding="utf-8-sig") as file:
    reader = csv.reader(file, delimiter=";")
    next(reader)  # Přeskočíme hlavičku
    for row in reader:
        title, author = row[0], row[1]
        books[title] = {"Autor": author, "Hodnocení": "Nenalezeno"}

# Spustíme prohlížeče
driver = webdriver.Chrome()

try:
    # Přihlásíme
    driver.get("https://www.cbdb.cz/prihlaseni")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "log_name"))).send_keys(USERNAME)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "log_pass"))).send_keys(PASSWORD)
    
    login_button = driver.find_element(By.NAME, "log")
    driver.execute_script("arguments[0].click();", login_button)
    
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.cbdb.cz/stream"))
    print("✅ Přihlášení OK!")

    # Přejdeme na stránku hodnocení
    driver.get("https://www.cbdb.cz/uzivatel-9541-faithe/hodnoceni")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
    print("✅ Načtena stránka hodnocení!")

    # Získání hodnocení pro každou knihu
    missing_ratings = []

    for title in books:
        try:
            # Najdeme knihu podle názvu
            book_element = driver.find_element(By.XPATH, f"//a[contains(text(), '{title}')]")
            book_row = book_element.find_element(By.XPATH, "./ancestor::tr")

            # Najdeme hodnocení podle obrázku hvězdiček
            star_element = book_row.find_element(By.XPATH, ".//img[contains(@src, 'star_mini_active.png')]")
            rating_percent = int(star_element.get_attribute("alt").replace("%", ""))

            # Převedeme procenta na hvězdičky
            books[title]["Hodnocení"] = rating_percent // 20

        except Exception:
            missing_ratings.append(title)

    # Uložíme do CSV
    output_file = "moje_knihy_s_hodnocenim.csv"
    with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Název", "Autor", "Hodnocení"])
        for title, data in books.items():
            writer.writerow([title, data["Autor"], data["Hodnocení"]])

    print(f"✅ Hodnocení uloženo do '{output_file}'!")
    
    if missing_ratings:
        print("⚠️ Nepodařilo se dohledat hodnocení pro tyto knihy:")
        for title in missing_ratings:
            print(f"   - {title}")

except Exception as e:
    print(f"❌ Chyba: {e}")

finally:
    driver.quit()