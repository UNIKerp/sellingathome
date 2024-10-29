import requests
from bs4 import BeautifulSoup
import time 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
# URL de Google Maps avec une requête de recherche
search_query = "restaurants à Dakar"
url = 'https://www.google.fr/maps'

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
response = driver.get(url)
wait = WebDriverWait(driver, 10)

search_bar =  wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]')))
print(search_bar)
if search_bar:
    print("Contenu de la barre de recherche :", search_bar.get_attribute('value'))
else:
    print("Barre de recherche non trouvée.")

