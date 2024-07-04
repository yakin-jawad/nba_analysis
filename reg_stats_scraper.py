from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time

def scrape_and_build(web, table_name, path, conn):
    
    # Initialize the Selenium web driver.
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)

    try: 

        driver.get(web)

        # Accepts cookies.
        try: 
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Accept')]"))).click()
        except:
            print("There are no cookies to accept.")

        # Closes newsletter.
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "bx-close-xsvg"))).click()
        except:
            print("There is no newsletter to close.")

        # Initializes the database.
        database = []

        while True:
            html = driver.page_source

            # Parses the HTML content of the table.
            soup = BeautifulSoup(html, 'html.parser')

            # Actually locates the table.
            table = soup.find('table', {'class': 'Crom_table__p1iZz'})

            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')[1:]
                player_stats = [cell.text.strip() for cell in cells]
                database.append(player_stats)
                
            try:
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Pagination_button__sqGoH[data-pos='next']")))
                next_button.click()
                time.sleep(2)
            except:
                print("No more pages to load. Scraping is complete!")
                break

        # Creates header columns.
        header = ['NAME', 'TEAM', 'AGE', 'GP', 'W', 'L', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%',
                '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST',
                'TOV', 'STL', 'BLK', 'PF', 'FP', 'DD2', 'TD3', '+/-']
        stats_df = pd.DataFrame(database, columns=header)
        
        # Converts the following columns to integers and floats respectively.
        ints = ['AGE', 'GP', 'W', 'L']
        stats_df[ints] = stats_df[ints].astype(int)
        floats = ['MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 
                    'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'FP',
                    'DD2', 'TD3', '+/-']
        stats_df[floats] = stats_df[floats].astype(float)
        
        # Bulk inserts the dataframe and converts into an SQL database.
        stats_df.to_sql(table_name, conn, if_exists='replace', index=False)
        
    except Exception as e:
        print(f"An error occurred: {e}")
            
    finally:
        driver.quit()

if __name__ == "__main__":

    # Creates a connection to the database.
    conn = sqlite3.connect('nba_database.db')
    
    base_url = 'https://www.nba.com/stats/players/traditional?Month={}&SeasonType=Regular+Season&Season=2023-24'
    path = '/Users/yakin.jawad/Programming/Projects/Database/chromedriver'
    
    for month in range(1, 8):
        month_url = base_url.format(month)
        table_name = f'reg_month_{month}'
        
        scrape_and_build(month_url, table_name, path, conn)
        
    # Closes the connection.
    conn.close()