"""
Project:        Dictator's Speeches Database
Module:         Speeches webscrapping
Author:         Carlos Alberto Toruño Paniagua
Date:           September 30th, 2023
Description:    This module is focused in extracting the speech transcripts of Daniel Ortega and Rosario Murillo.
                The scripts are available online on www.el19digital.com as of September, 2023
This version:   September 30th, 2023
"""

import pandas as pd
import requests
import time
import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

##============================##
## EXTRACTING SPEECHES URLs   ##
##============================##

# Local path to chromium binary
bin_path = "C:/Users/ctoruno/Documents/Chromium/chrome.exe"

# Opening website from webdriver  
driver   = webdriver.Chrome()

# Create action chain object
action = ActionChains(driver)

# Defining a waiting period for elements to be clickable
wait = WebDriverWait(driver, 10)

# Defining a function to extract URLs from a dynamic page
def url_extract(base_url, npages):

    """
    Takes a URL for a dynamic website along with the total number of
    pages within their pagination widget and returns a list containing
    all the individual links within all those pages.
    """

    # Creating an empty list to store results
    links = []

    # Looping across pages
    for page in range(1, npages+1):

        print("Currently extracting links from page no. " + str(page))
        time.sleep(2)

        # Fetching source code
        content = driver.page_source

        # Parcening the retrieved code
        soup = BeautifulSoup(content, "lxml")

        # Creating a list with all the box elements
        boxes = (soup
                 .find("div", class_ = "tg-row")
                 .find_all("div", class_ = "tg-col-control"))
            
        # Looping across boxes to get individual links
        for box in boxes:
            URL   = box.find("h3").find("a").get("href")

            # Appending URL to link list
            links.append(URL)

        # Clicking on defined element
        def nextpageplease(locator = "Siguiente →"):

            # Locate element
            xpath = '//*[@id="post-458"]/div[1]/div[2]/section[2]/div/div[1]/div/div/div/div'
            next_button = driver.find_element(By.XPATH, xpath)

            # Move to element
            driver.execute_script("arguments[0].scrollIntoView();", next_button)

            # Clik on NEXT PAGE button
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, locator))).click()
        
        try:
            nextpageplease()
        except:
            print("Not able to extract move on... trying again")

    return links

# Extacting speeches given by Rosario Murillo
romu_url = "https://www.canal4.com.ni/rosario-murillo/"
driver.get(romu_url)
romu_links = url_extract(base_url = base_url, npages = 145)

# Extacting speeches given by Rosario Murillo & Daniel Ortega
rmdo_url = "https://www.canal4.com.ni/discurso-daniel-y-rosario/"
driver.get(rmdo_url)
rmdo_links = url_extract(base_url = base_url, npages = 28)

# Saving links as a CSV file
all_links = romu_links + rmdo_links
path2data = os.getcwd() + "\\..\\..\\Data\\rmdo_links.csv"
df = pd.DataFrame(all_links)
df.to_csv(path2data, index = False, encoding = "utf-8")


##============================##
## EXTRACTING SPEECH CONTENT  ##
##============================##

# Defining headers
agent   = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ",
           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
           "96.0.4664.110 Safari/537.36"]
headers = {
    "User-Agent": "".join(agent)
}

def extract_content(url_list):
    """
    Takes a list of URLs and returns a dataframe with the content extracted
    from the URL.

    Title, date, content and URL.
    """

    results = []

    for url_link in url_list:
        
        time.sleep(2)

        # Fetching source code
        response = requests.get(url_link, headers = headers)

        # Parsening code
        soup = BeautifulSoup(response.text, "lxml")

        # Retrieving information
        headline = soup.find("h1").text
        headline = re.sub("\n", "", headline)

        date = (soup
                .find("span", class_ = "posted-on")
                .find("time")
                .get("datetime"))
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").date()

        body = (soup
                .find("div", class_ = "entry-content clearfix")
                .find_all("p"))
        
        content = [p.text for p in body]
        content = " ".join(content)

        # Defining dictionary entry
        speech = {
            "headline" : headline,
            "date"     : date,
            "content"  : content,
            "url"      : url_link
        } 
        
        # Appending to main list
        results.append(speech)

    # Converting to Data Frame
    data = pd.DataFrame(results)

    return data

# Applying function to extract data
data = extract_content(all_links)

# Saving data
path2data = os.getcwd() + "\\..\\..\\Data\\master_data.csv"
data.to_csv(path2data, 
            index    = False, 
            encoding = "utf-8")
path2data = os.getcwd() + "\\..\\..\\Data\\master_data.xlsx"
data.to_excel(path2data)