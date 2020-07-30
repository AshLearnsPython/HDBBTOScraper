from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pprint
import re
import pandas as pd
import os
import sys
import time
import openpyxl as op


#Initialization#
os.chdir(r'C:\Users\User\Desktop\Programming\Python')

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.maximize_window()

driver.get("https://services2.hdb.gov.sg/webapp/BP13AWFlatAvail/BP13EBSFlatSearch?Town=Toa+Payoh&Flat_Type=BTO&selectedTown=Toa+Payoh&Flat=2-Room+Flexi+%28Short+Lease%29&ethnic=Y&ViewOption=A&projName=A&Block=0&DesType=A&EthnicA=Y&EthnicM=&EthnicC=&EthnicO=&numSPR=&dteBallot=202002&Neighbourhood=&Contract=&BonusFlats1=N&searchDetails=Y&brochure=true")

#Function to close the advertisment popup#

wait = WebDriverWait(driver, 15)
wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/header/div[3]/div/a/span[1]")))

FirstLineBlocks = driver.find_element_by_xpath("/html/body/header/div[3]/div/a/span[1]").click()
time.sleep(5)

#Setup of variables and lists#

td = 1
td2 = 1

streetList= []
blockList = []
unitList = []
priceList = []
yearList = []

#Selenium - Find the first row of the text block#
#Nested in a range of 7, because there are max 7 hyperlinks per row. In the event that there are only <7 hyperlinks, we put in a try function#
#This will click each block hyperlink, to display the total units available#
#I used Selenium because the HDB website is Javascript-heavy and prevented me from just using beautifulsoup#

for i in range(7):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/form[1]/div[4]/div[1]/div/div[7]/div[1]/table/tbody/tr[1]/td["+str(td)+"]/div"))
        )
        time.sleep(3)
        FirstLineBlocks = driver.find_element_by_xpath("/html/body/form[1]/div[4]/div[1]/div/div[7]/div[1]/table/tbody/tr[1]/td[" + str(td) + "]/div/font/a/font").click()

        td += 1

    except Exception as e:
        print(e)
        continue

#After each hyperlink is clicked, there is a list of units available. I then used BeautifulSoup to scrape the html of the existing page.#
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    #finding block details, block name, street name, release date#
    tableRow = soup.find('div', {"id": "blockDetails"})

    blockName = tableRow.find('div',class_="large-3 columns").text.strip()
    streetName = tableRow.find('div',class_="large-5 columns").text.strip()
    completionYear = tableRow.find('div',class_="large-7 columns").text.strip()

    #In the HDB website, the unit no. and price were kept in tooltips which only appeared when the mouse hovered over
    #each unit. Instead of making Selenium hover over each hyperlink, we scrape the HTML to find the price and unit no.#
    tooltips = soup.find_all('span', {"class": "tooltip tip-bottom"})

    #finding the unit name and associated price for 99years via Regular Expressions#
    #tooltips[5:] because the first 4 entries which have the class "toolip" are not related to units, so we skip them#
    for tooltip in tooltips[5:]:
        pattern = re.compile(r"""data-selector=(\S+).*(\$\d+,\d{3})( - (.*Years))?""")
        extract = pattern.findall(str(tooltip))

        res = list(zip(*extract))

        unit = str(res[0])
        unitstr = unit.strip('\"\'(\"\',)')

        price = str(res[1])
        pricestr = price.strip('(\'\$,\',)')

    #years2 required as the strip function does not full strip some areas#
        years = str(res[3])
        yearstr = years.strip('(\') Years\')\'')
        years2 = yearstr[0:2]

    #Appending to lists  and preparing the dataframe#
        streetList.append(streetName)
        blockList.append(blockName)
        unitList.append(unitstr)
        priceList.append(pricestr)
        yearList.append(years2)


print("First row")


#Perform the same actions for the second row of the HDB list#
for i in range(7):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/form[1]/div[4]/div[1]/div/div[7]/div[1]/table/tbody/tr[2]/td["+str(td2)+"]/div"))
        )
        time.sleep(3)
        FirstLineBlocks = driver.find_element_by_xpath("/html/body/form[1]/div[4]/div[1]/div/div[7]/div[1]/table/tbody/tr[2]/td[" + str(td2) + "]/div/font/a/font").click()

        td2 += 1

    except Exception as e:
        print(e)
        continue

    #saving html source and finding tool tip text in each page#
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    #finding block details, block name, street name, release date#
    tableRow = soup.find('div', {"id": "blockDetails"})

    blockName = tableRow.find('div',class_="large-3 columns").text.strip()
    streetName = tableRow.find('div',class_="large-5 columns").text.strip()
    completionYear = tableRow.find('div',class_="large-7 columns").text.strip()

    tooltips = soup.find_all('span', {"class": "tooltip tip-bottom"})

    #finding the unit name and associated price for 99years#
    for tooltip in tooltips[5:]:
        pattern = re.compile(r"""data-selector=(\S+).*(\$\d+,\d{3})( - (.*Years))?""")
        extract = pattern.findall(str(tooltip))

        res = list(zip(*extract))

        unit = str(res[0])
        unitstr = unit.strip('\"\'(\"\',)')

        price = str(res[1])
        pricestr = price.strip('(\'\$,\',)')

        years = str(res[3])
        yearstr = years.strip('(\') Years\')\'')
        years2 = yearstr[0:2]

        streetList.append(streetName)
        blockList.append(blockName)
        unitList.append(unitstr)
        priceList.append(pricestr)
        yearList.append(years2)


#append to dataframe dictionary#
data_set = pd.DataFrame(
    {'Street': streetList,
     'Block': blockList,
     'Unit': unitList,
     'Price': priceList,
     'Lease': yearList
    }
)

#save to excel#
data_set.to_excel('hdboutput.xlsx')

print("Completed")
