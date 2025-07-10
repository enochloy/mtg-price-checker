# import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3

from time import sleep
import random
import re


def scrape_agora():
    # open browser
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("https://agorahobby.com/store/mtg")

    # obtain list of urls
    urls = []
    elements = driver.find_elements(By.CLASS_NAME, "sn_lvl1navi")
    for element in elements:
        href = element.find_element(By.CLASS_NAME, "sn_toplink").get_attribute("href")
        
        if not href.endswith("#"):
            urls.append(href)
        else:
            inner_elements = element.find_elements(By.CLASS_NAME, "sn_link")
            for inner_element in inner_elements:
                urls.append((inner_element.get_attribute("href")))
                
    # quit driver
    driver.quit()

    # create empty list
    agora = []

    # loop through urls
    for url in urls:
        # open browser and wait 2s
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get(url)
        sleep(5)

        while True:
            try:
            # click on loadmore
                loadmore = driver.find_element(By.ID, "list_loadmore")
                loadmore.click()
                sleep(2)
            # once it hit ends of the page
            except Exception as e:
                print(f"Error clicking 'loadmore': {e}")
                break

        item_names = driver.find_elements(By.CLASS_NAME, "store-item-title")
        item_prices = driver.find_elements(By.CLASS_NAME, "store-item-price")
        for name, price in zip(item_names, item_prices):
            temp_dict = {}
            temp_dict['name'] = name.text
            temp_dict['price'] = float(price.text.replace('$', ''))
            agora.append(temp_dict)
        print(f"{url} is done!")
        print(agora[-1])
        
        driver.quit()

    # save agora as csv
    agora = pd.DataFrame(agora)
    agora['store'] = 'agora'
    
    return agora

def scrape_onemtg():
    # Indicate base url
    url = 'https://onemtg.com.sg/collections/mtg-singles-instock'
    base_url = 'https://onemtg.com.sg/collections/mtg-singles-instock?page='
    response = requests.get(url)
    response.status_code

    soup = BeautifulSoup(response.text, 'lxml')
    num_pages = int(soup.find_all('div', class_='pages')[-1].text)

    # create empty list
    onemtg = []

    # scraping
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]

    for i in range(num_pages):
        headers = {'User-Agent': random.choice(user_agent_list)}
        response = requests.get(base_url + str(i+1), headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('div', class_='product Norm')
        
        for item in items:
            temp_dict = {}
            title = item.find_all('p', class_='productTitle')[0].text.replace('\r\n', '').strip()
            price = item.find_all('p', class_='productPrice')[0].text.replace('\r\n', '').replace('$', '').replace(',', '').strip()
            if price == 'Varies':
                item_name = item.find_all('div', class_='addNow single')[0].text
                match = re.search(r'\$([\d.]+)', item_name)
                if match:
                    price = match.group(1)
            temp_dict['name'] = title
            temp_dict['price'] = float(price)
            onemtg.append(temp_dict)
        
        sleep(random.uniform(2,5))

    # create onemtg dataframe, convert price to float and create store column
    onemtg = pd.DataFrame(onemtg)
    onemtg['store'] = 'onemtg'

    return onemtg

def scrape_cardscitadel():
    # Indicate base url
    url = 'https://cardscitadel.com/collections/mtg-singles-instock'
    base_url = 'https://cardscitadel.com/collections/mtg-singles-instock?page='
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    } 
    response = requests.get(url, headers=headers)

    # print number of pages
    soup = BeautifulSoup(response.text, 'lxml')
    num_pages = int(soup.find_all('div', class_='pages')[-1].text)

    # create empty list
    citadel = []

    # scraping
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]

    for i in range(num_pages):
        headers = {'User-Agent': random.choice(user_agent_list)}
        response = requests.get(base_url + str(i+1), headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('div', class_='product Norm')
        
        for item in items:
            temp_dict = {}
            title = item.find_all('p', class_='productTitle')[0].text.replace('\r\n', '').strip()
            price = item.find_all('p', class_='productPrice')[0].text.replace('\r\n', '').replace('$', '').replace(',', '').strip()
            if price == 'Varies':
                item_name = item.find_all('div', class_='addNow single')[0].text
                match = re.search(r'\$([\d.]+)', item_name)
                if match:
                    price = match.group(1)
            temp_dict['name'] = title
            temp_dict['price'] = float(price)
            citadel.append(temp_dict)
        
        sleep(random.uniform(2,5))

    # cleaning dataframe
    citadel = pd.DataFrame(citadel)
    citadel['store'] = 'citadel'

    return citadel

def scrape_greyogre():
    # Indicate base url
    url = 'https://www.greyogregames.com/search?page=1&q=**'
    base_url = 'https://www.greyogregames.com/search?page={}&q=**'
    response = requests.get(url)

    # print number of pages
    soup = BeautifulSoup(response.text, 'lxml')
    page_list = []
    for anchor in soup.find_all('ol', class_='pagination')[0].find_all('a'):
        if match := re.search(r'(\d+)', anchor.text):
                page_list.append(int(match.group(1)))
    num_pages = max(page_list)

    # create empty list
    ogre = []

    # scraping
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]

    for i in range(num_pages):
        headers = {'User-Agent': random.choice(user_agent_list)}
        response = requests.get(base_url.format(i+1), headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('div', class_='productCard__lower')
        
        for item in items:
            name = item.find('p', class_='productCard__title').text.strip()
            price = item.find('p', class_='productCard__price').text.replace('$', '').replace('SGD', '').replace(',','').strip()
            try:
                price = float(price)
            except ValueError as e:
                print(e)
            ogre.append({
                'name': name,
                'price':price,
            })
        
        sleep(random.uniform(1,2))

    # cleaning dataframe
    ogre = pd.DataFrame(ogre)
    ogre['store'] = 'greyogre'
    ogre = ogre.drop(ogre_df[ogre_df['price'] == ''].index).reset_index(drop=True)
    ogre['price'] = ogre['price'].astype(float)
    
    return ogre


def combine_and_update_db(dataframes):
    # combine dataframes, drop those with price == 0 and art cards
    combined = pd.concat(dataframes).dropna().reset_index(drop=True)
    combined = combined.drop(combined[combined['price'] == 0].index).reset_index(drop=True)
    combined = combined.drop(combined[combined['name'].str.lower().str.contains('art card')].index)

    # Establish a connection to the SQLite database.
    conn = sqlite3.connect('./newcards.db')

    # Create a cursor object to execute SQL commands.
    cur = conn.cursor()

    # Create the 'cards' table if it doesn't already exist.
    # It has columns for id (primary key), card name, price, and store.
    cur.execute("""CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    store TEXT NOT NULL
    );""")

    # If you're running this multiple times to update data,
    # DELETE existing data from the 'cards' table before inserting new data,
    # cur.execute("DELETE FROM cards;")

    # Iterate over each row in the combined DataFrame.
    # Insert the card's name, price, and store into the 'cards' table.
    for _, row in combined.iterrows():
        conn.execute("INSERT INTO cards (name, price, store) VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def run_all_scrapers():
    agora_data = scrape_agora()
    onemtg_data = scrape_onemtg()
    cardscitadel_data = scrape_cardscitadel()
    ogre_data = scrape_greyogre()
    
    # Combine data and update database 
    combine_and_update_db([agora_data, onemtg_data, cardscitadel_data, ogre_data])
    print("Scraping and database update complete!")

if __name__ == "__main__":
    run_all_scrapers()