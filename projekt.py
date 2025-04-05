import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

USERNAME = "username" # Doplň uživatelské jméno
PASSWORD = "password" # Doplň heslo

driver = webdriver.Chrome()

try:
    # Přihlásíme se
    driver.get("https://www.cbdb.cz/prihlaseni")

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "log_name"))).send_keys(USERNAME)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "log_pass"))).send_keys(PASSWORD)
    
    login_button = driver.find_element(By.NAME, "log")
    driver.execute_script("arguments[0].click();", login_button)

    WebDriverWait(driver, 10).until(EC.url_contains("https://www.cbdb.cz/stream"))
    print("✅ Přihlášení OK!")

    # Otevřeme seznam knih
    base_url = "https://www.cbdb.cz/moje-knihy?booklist=2"
    driver.get(base_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
    print("✅ Načten seznam knih!")

    books_dict = {}
    visited_pages = set()

    def scrape_page():
        """Funkce, která stáhne VŠECHNY knihy z aktuální stránky a správně získává žánr."""
        genre_headings = driver.find_elements(By.CLASS_NAME, "mt-3")  # Seznam všech nadpisů žánrů (h2.mt-3)
        book_elements = driver.find_elements(By.CLASS_NAME, "col-6.col-sm-4.col-md-3")  # Všechny knihy na stránce

        current_genre = "Neznámý žánr"

        for element in driver.find_elements(By.XPATH, "//*"):  # Projdeme všechny elementy na stránce
            if element in genre_headings:
                current_genre = element.text.strip()  # Pokud je to žánrový nadpis, aktualizujeme žánr
            elif element in book_elements:
                try:
                    title = element.find_element(By.CLASS_NAME, "my_books_item_name").text.strip()
                    author = element.find_element(By.CLASS_NAME, "my_books_item_authors").text.strip()
                    book_key = (title, author)

                    if book_key in books_dict:
                        books_dict[book_key]["Žánry"].add(current_genre)
                        continue

                    book_data = {
                        "Žánry": {current_genre},
                        "Nakladatelství": "nenalezeno",
                        "Rok vydání": "nenalezeno",
                        "Datum přečtení": "nenalezeno"
                    }

                    # Klikneme na tlačítko pro detaily
                    try:
                        toggle_button = element.find_element(By.CLASS_NAME, "my_books_about_button")
                        book_id = toggle_button.get_attribute("id-attr")
                        driver.execute_script("arguments[0].click();", toggle_button)

                        details_box = WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, f"my_books_about_box_{book_id}"))
                        )

                        release_info = details_box.find_element(By.CLASS_NAME, f"my_books_release_{book_id}").text.strip()
                        date_info = details_box.find_element(By.CLASS_NAME, f"my_books_time_{book_id}").text.strip()

                        if " / " in release_info:
                            publisher, year = release_info.split(" / ")
                            book_data["Nakladatelství"] = publisher
                            book_data["Rok vydání"] = year

                        book_data["Datum přečtení"] = date_info

                    except Exception as e:
                        print(f"⚠️ Chyba detailů: {title}: {e}")

                    books_dict[book_key] = book_data

                except Exception as e:
                    print(f"⚠️ Chyba knihy: {e}")

    # Scrapujeme první stránku
    current_page = 1
    visited_pages.add(current_page)

    scrape_page()

    # Přejdeme na další stránky
    while True:
        try:
            pagination_links = driver.find_elements(By.CSS_SELECTOR, ".pagination_item")

            page_numbers = []
            for link in pagination_links:
                try:
                    page_num = int(link.text.strip())
                    page_numbers.append(page_num)
                except ValueError:
                    continue

            if not page_numbers:
                print("✅ Žádné další stránky, konec scrapování.")
                break

            max_page = max(page_numbers)

            if current_page >= max_page:
                print("✅ Dosáhli jsme poslední stránky.")
                break

            next_page_num = current_page + 1
            next_page_link = driver.find_element(By.XPATH, f"//a[contains(@href, 'booklist=2&page={next_page_num}')]")

            if next_page_num in visited_pages:
                print(f"⚠️ Stránka {next_page_num} už byla navštívena, přeskakuji!")
                break

            driver.execute_script("arguments[0].click();", next_page_link)
            time.sleep(2)

            WebDriverWait(driver, 5).until(EC.url_contains(f"page={next_page_num}"))
            current_page = next_page_num
            visited_pages.add(current_page)

            scrape_page()

        except Exception as e:
            print(f"⚠️ Chyba při přechodu na další stránku: {e}")
            break

    # Uložíme do CSV
    filename = "moje_knihy.csv"
    with open(filename, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Název", "Autor", "Žánry", "Nakladatelství", "Rok vydání", "Datum přečtení"])

        for (title, author), data in books_dict.items():
            writer.writerow([
                title, 
                author, 
                ", ".join(data["Žánry"]),
                data["Nakladatelství"], 
                data["Rok vydání"], 
                data["Datum přečtení"]
            ])

    print(f"✅ Testovací soubor '{filename}' vytvořen!")

except Exception as e:
    print(f"❌ Chyba: {e}")

finally:
    driver.quit()