# scraper

import requests, re, datetime, time, sys, csv
import glob
import os
import itertools
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from splinter import Browser
from random import seed, random

from settings import CHROMEDRIVER_DIR

def strip_html(stringOfHtml, check):
    while check == False:
        stringOfHtml_ = re.sub("<.*?>", "", str(stringOfHtml))
        if "<" in stringOfHtml_:
            strip_html(str(stringOfHtml_), False)
        else:
            check = True
    return re.sub("amp;", "", str(stringOfHtml_))

def extract_href(stringOfHtml):
    # print("checking links:")
    stringOfHtml_ = re.findall("(?:href=\".*?\")", str(stringOfHtml), re.I|re.M)
    try:
        # print(stringOfHtml_[0])
        res = re.sub("href=|\"","",stringOfHtml_[0])
    except:
        # print(stringOfHtml_)
        res = stringOfHtml_
    return res

def scraper(query):
    # define the location of the Chrome Driver - CHANGE THIS!!!!!
    executable_path = {'executable_path': CHROMEDRIVER_DIR}

    # Create a new instance of the browser, make sure we can see it (Headless = False)
    browser = Browser('chrome', **executable_path, headless=False)

    # define the components to build a URL
    method = 'GET'

    url = "https://www.google.com"
    # build the URL and store it in a new variable
    p = requests.Request(method, url).prepare()
    myurl = p.url

    # go to the URL
    browser.visit(myurl)
    seed(1)
    time.sleep(random()+1)
    browser.driver.set_window_size(1920, 1080)
    time.sleep(random()+1)
    query = query + "\n"
    browser.fill("q", query)
    time.sleep(random()+1)

    # add a little randomness to using the page
    time.sleep(random()+random()*10+2)

    maps_links = browser.links.find_by_partial_href("maps.google.com")
    maps_links[0].click()
    time.sleep(random()+random()*10+2)

    next_page_button_xpath = '''//*[@id="n7lv7yjyC35__section-pagination-button-next"]'''
    next_page_button = browser.find_by_xpath(next_page_button_xpath)

    html = browser.html

    # pagination
    x = 0
    while x < 2:
        try:
            next_page_button.click()
            time.sleep(random()+random()*10+4)
            html += browser.html
        except:
            print("Error occurred with pagination: ", sys.exc_info())
            pass
        x += 1

    soup = BeautifulSoup(html, "html.parser")

    
    info = [[],[],[],[],[],[]] # for storing all the info that's about to be parsed

    x = len(soup.find_all('div', class_='section-result'))
    y = 0
    while y < x:
        try:
            entries = soup.select('div.section-result-text-content')
            biz_name = strip_html(entries[y].select('h3')[0], False)
            ph_num = strip_html(entries[y].select('span.section-result-phone-number')[0], False)
            location = strip_html(entries[y].select('span.section-result-location')[0], False)
            rating = strip_html(entries[y].select('span.cards-rating-score')[0], False)
            review_num = strip_html(entries[y].select('span.section-result-num-ratings')[0], False)
            if biz_name != "":
                info[0].append(biz_name)
            else: 
                info[0].append("none")
            if ph_num != "":
                info[1].append(ph_num)
            else: 
                info[1].append("none")
            if location != "":
                info[2].append(location)
            else: 
                info[2].append("none")
            if rating != "":
                info[3].append(rating)
            else: 
                info[3].append("none")
            if review_num != "":
                info[4].append(review_num)
            else: 
                info[4].append("none")

            links = soup.select('div.section-result-action-container')
            link_ = extract_href(links[y])
            if isinstance(link_, str):
                if link_ == "":
                    info[5].append("none")
                else:
                    info[5].append(link_)
            else:
                info[5].append("none")
            
        except:
            print(f"error with printing an entry: {sys.exc_info()}")
            pass
        y+=1
    # print(info)

    

    date = datetime.datetime.now()
    local_date = date.strftime("%x").replace("/", "_")
    local_time = date.strftime("%X").replace(":", "")
    query = query.replace(" ", "-").replace("\n", "")
    file_string = f"./results/{local_date}-{local_time}-{query}.csv"

    Path(file_string).touch()

    with open(file_string, 'w', newline="") as csvfile:
        fieldnames = ['Business Name', 'Ph. Number', 'Location', 'Rating', 'Reviews', 'Website']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    csvfile.close()
    
    time.sleep(3)

    browser.quit()

    df=pd.read_csv(file_string)

    # print(len(info[0]))
    # print(len(info[1]))
    # print(len(info[2]))
    # print(len(info[3]))
    # print(len(info[4]))
    # print(len(info[5]))

    for (a,b,c,d,e,f) in itertools.zip_longest(info[0], info[1], info[2], info[3], info[4], info[5]):
        print(f"biz: {a} / phone: {b} / location: {c} / ratings: {d} / reviews: {e} / site: {f}")
        row = [a,b,c,d,e,f]
        df.loc[len(df.index)] = row

    print("from scraper.py:")
    print(df.head())
    # print(df.dtypes)


    df.to_csv(path_or_buf=file_string)

    return 

scraper("bike shop near me")
