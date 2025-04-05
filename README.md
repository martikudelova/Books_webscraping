# Datová analýza přečtených knih

V rámci projektu pro Engeto jsem se rozhodla vytvořit vlastní dataset pro vizualizaci v Power BI. Jako zdroj dat jsem zvolila svůj čtenářský profil na jednom knihovním portálu, kde eviduji přečtené knihy. Jelikož portál neumožňuje exportovat potřebné informace v dostatečném rozsahu, vytvořila jsem pomocí Pythonu několik skriptů, které data automatizovaně získávají.

> **Poznámka:** Název portálů zde neuvádím, protože si nejsem jistá, zda výslovně povolují web scraping, ale v kódu je ponechám 😊

## 🛠️ Použité knihovny

- `selenium` – automatizace prohlížeče a práce s dynamickými webovými prvky  
- `csv` – čtení a zápis do souborů  
- `time` – zpoždění při scrapování  

---

## 📁 Přehled skriptů

### `projekt.py`

Tento skript:
- se přihlásí do uživatelského profilu,
- přejde na stránku se seznamem přečtených knih podle žánrů,
- z každé sekce (žánru) získá:
  - název knihy,
  - autora/autory,
  - žánr (z nadpisu sekce),
  - nakladatelství, rok vydání a datum přidání (z vyskakovacích prvků).

Pokud je kniha zařazena do více žánrů, objeví se v CSV souboru pouze jednou. Ve sloupci **Žánry** jsou jednotlivé žánry oddělené čárkou.

Skript také sleduje, které stránky už byly zpracovány a ukládá výsledky do `.csv` souboru.

---

### `update.py`

Později jsem zjistila, že na původním portálu je uveden pouze rok posledního vydání. Tento skript:
- načte původní CSV soubor,
- pro každou knihu vyhledá:
  - rok **prvního** vydání,
  - počet stran,
- doplní tyto informace zpět do dat.

---

### `update_hodnoceni.py`

Skript pro doplnění mého hodnocení knih:
- načte updatovaný CSV soubor
- hodnocení převede z procent na škálu 1–5, viz níže,
- zároveň ověří, které knihy jsem zapomněla ohodnotit,
- doplní tyto informace zpět do dat.

| Počet hvězd | Procenta |
|-------------|----------|
| 1 hvězda    | 20 %     |
| 2 hvězdy    | 40 %     |
| 3 hvězdy    | 60 %     |
| 4 hvězdy    | 80 %     |
| 5 hvězd     | 100 %    |

---

### `autori.py`

Skript pro doplnění národností autorů:
- načte jména z CSV souboru, kde jsou uvedena unikátní jména autorů,
- vyhledá každého z nich v online databázi,
- doplní národnost.

---

## 🤖 S čím mi pomohla AI (ChatGPT)

1. **Přihlášení a scraping s interaktivními prvky:**
   - doporučení Selenia a ChromeDriveru,
   - doporučení Time pro zpoždění scrapování / čekání, než se načtou prvky,
   - získání informací z prvků po kliknutí (např. datum přidání knihy).

2. **Scraping HTML elementů:**
   - porozumění HTML struktuře a selektorům z dodaných screenshotů

3. **Řešení duplikací knih ve více žánrech:**
   - použití `set` a `dict` místo klasických seznamů.

4. **Zacyklení při stránkování:**
   - nalezení celkového počtu stránek,
   - sledování již zpracovaných.

5. **Problémy s diakritikou:**
   - použití `utf-8-sig` pro správné zobrazení češtiny.

---

## ⚠️ Známé nedostatky

- **Duplikace autorů:** Autorské dua u různých knih v různém pořadí způsobily duplikáty v `.csv` s unikátními jmény autorů.
- **Nesrovnalosti v názvech:** Některé knihy měly na různých portálech jiné názvy (např. přidaný název série nebo římské číslice u pokračování).
- **Formát jmen autorů:** Jeden portál uváděl plná jména, druhý iniciály nebo pseudonymy způsobily problémy při updatování dat.
- **Záměna jazykových verzí:** Např. anglický název na webu dohledal český překlad a vyscrapoval jiný rok vydání a počet stran.
- **Nejednotnost národností:** Národnost ukazovala údaje jako „Česko“, „Londýn, UK“ nebo „Spangler, Pensylvánie, USA“. Proto jsem je upravila tak, že jsem si ponechala jen poslední položku za čárkou (např. „USA“).
- **Chybějící anglické knihy:** Mnoho přečtených anglických knih nemám v datasetu zahrnuty, jelikož nejsou uvedené na CZ portálu a nemají ani český překlad. Bylo by možné je doplnit z mého profilu na Goodreads, ale jelikož pro projekt v Power BI nepotřebuji přesný seznam, tak to v tuto chvíli doplňovat nebudu.
- **Chybné datum přečtení:** Knihám s datem přečtení `1.1.1970`(což značí chybějící údaj, pravděpodobně ještě na portálu nesledovali datum přidání do seznamu přečtených knih) jsem přiřadila náhodné datum z intervalu:
  - mezi datem prvního vydání (nebo mým věkem cca 12 let, kdy jsem začala aktivně číst),
  - a 14. 11. 2014 (datum, od kterého zhruba portál začal sledovat datum přečtení).

---

## 📌 Závěr

Tento projekt mi umožnil propojit programování s mým čtenářským koníčkem a vytvořit si vlastní datový soubor pro analýzu knih v Power BI. Skripty lze snadno upravit a přizpůsobit pro jiné uživatele.

---

