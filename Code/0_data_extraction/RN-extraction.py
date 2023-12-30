#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 13:28:09 2022

@author: carlostorunopaniagua
"""

# Libraries needed
import pandas as pd
# import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Header definition
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

# Setting up a Selenium webdriver
driver = webdriver.Chrome(executable_path = '/Users/carlostorunopaniagua/Documents/GitHub/chromedriver_mac64')

# Getting speeches links from root pages
article_links = []
for page in range(1,26):
    driver.get(f'https://radionicaragua.com.ni/category/discurso/page/{page}/')
    content = driver.page_source
    soup = BeautifulSoup(content)

    articlelist = soup.findAll("article")
    for article in articlelist:
        for caption in article.findAll("figcaption"):  
            for atags in caption.findAll("a", href=True):
                print(atags["href"])
                article_links.append(atags["href"])

# Extracting information from individual links
speeches_list = []
for link in article_links:
    driver.get(link)
    content = driver.page_source
    soup = BeautifulSoup(content)

    article_title = soup.find("h1", class_ = "title-to-share entry-title mb-2 pb-4").text.strip()
    article_date = soup.find("div", class_ = "d-flex entry-date justify-content-end").text.strip()
    article_content = []
    prgphs = soup.select(".entry-content p+ p")
    for p in prgphs:
        # article_content = article_content + p + " "
        article_content.extend(p.stripped_strings)
    article_content = " ".join(article_content)
        
    
    speech = {
        "title"  : article_title,
        "date"   : article_date,
        "speech" : article_content,
        "link"   : link
        }
    
    speeches_list.append(speech)

# Saving data into a dataframe    
master_data = pd.DataFrame(speeches_list)
master_data.to_csv("Data/master.csv", index = False, encoding = "utf-8")
