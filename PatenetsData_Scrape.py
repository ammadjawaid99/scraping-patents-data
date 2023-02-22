# -*- coding: utf-8 -*-
"""

@author: Ammad
"""

location = r'change location here'
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import time
import math

import warnings
warnings.filterwarnings('ignore')
#chrome_options = Options()
#chrome_options.add_argument('--headless')


# =============================================================================
# # THis part of the code opens the chrome and the website from which we want to extract data
# =============================================================================
link = 'https://www.freepatentsonline.com/result.html?p=01&srch=xprtsrch&query_txt=PT%2FD+and+PD%2F07%2F25%2F2022-%3E10%2F25%2F2022&uspat=on&date_range=all&stemming=on&sort=relevance'

patentDetails = {}	
index = 0

driver = webdriver.Chrome(location + '//chromedriver.exe')
driver.get(link)

patentLinks = []
totalRecords = int(driver.find_element(By.XPATH, "//div[@class = 'well well-small']//table//td").text.split(' ')[-1])
totalPages = math.ceil(totalRecords/50)

for i in range(1, totalPages + 2):
	pagesLink = driver.find_elements(By.XPATH, "//div[@class = 'well well-small']//table//td//a")
	patentLinksElement = driver.find_elements(By.XPATH, "//table[@class = 'listing_table']//td/a")
	
	for linkElement in patentLinksElement:
		link = linkElement.get_attribute("href")
		patentLinks.append(link)
	
	# Click on next page button
	time.sleep(3)
	driver.execute_script("arguments[0].click();", pagesLink[-1])

# Store the patent links in a text file
with open(location + '\\patentLinks3.txt', 'w') as fp:
    for item in patentLinks:
        # write each item on a new line
        fp.write("%s\n" % item)
    print('Done')
	
# START HERE
driver = webdriver.Chrome(location + '//chromedriver.exe')
# Getting the data from each of the links
for patent in patentLinks:
	driver.get(patent)
	time.sleep(1)
	allDetails = driver.find_elements(By.XPATH, "//*[contains(text(), 'Title')]/../following-sibling::div")
	data = []
	for details in allDetails:
		data.append(details.text)
	
	try:
		documentNumber = data[0].split(' ')[-1]
	except:
		documentNumber = ''
	try:
		publicationDate = [x for x in data if 'Publication Date:' in x][0].split('\n')[1]
	except:
		publicationDate = ''
	try:
		filingDate = [x for x in data if 'Filing Date:' in x][0].split('\n')[1]
	except:
		filingDate = ''
	try:
		inventorName = ('\n').join([x for x in data if 'Inventors:' in x][0].split('\n')[1:])
	except:
		inventorName = ''
	try:
		assignee = ('\n').join([x for x in data if 'Assignee:' in x][0].split('\n')[1:])
	except:
		assignee = ''
	try:
		attorney = ('\n').join([x for x in data if 'Attorney, Agent or Firm:' in x][0].split('\n')[1:])
	except:
		attorney = ''
	
	patentDetails[index] = [publicationDate, filingDate, documentNumber, inventorName, assignee, attorney]
	
	index = index + 1
	print(index)
	
print('1 link is done')

df = pd.DataFrame.from_dict(patentDetails).transpose()
df.columns = ['publication_date', 'filing_date', 'document-number', 'inventor_name', 'assignee_name', 'attorney_name']
df = df.drop_duplicates('document-number')

# =============================================================================
# # Patent-Table
# =============================================================================
patentsTable = df[['publication_date', 'filing_date', 'document-number']]
patentsTable['patent_id'] = np.arange(1, len(df) + 1)
patentsTable = patentsTable[['patent_id', 'publication_date', 'filing_date', 'document-number']]

# =============================================================================
# # Inventors-Table
# =============================================================================
inventorsTable = df[['inventor_name']]
inventorsTable['inventor_id'] = pd.factorize(inventorsTable['inventor_name'])[0] + 1
inventorsTable = inventorsTable[['inventor_id', 'inventor_name']]

# =============================================================================
# # Assignees-Table
# =============================================================================
assigneesTable = df[['assignee_name']]
assigneesTable['assignee_id'] = pd.factorize(assigneesTable['assignee_name'])[0] + 1
assigneesTable = assigneesTable[['assignee_id', 'assignee_name']]

# =============================================================================
# # Attorneys-Table
# =============================================================================
attorneysTable = df[['attorney_name']]
attorneysTable['attorney_id'] = pd.factorize(attorneysTable['attorney_name'])[0] + 1
attorneysTable = attorneysTable[['attorney_id', 'attorney_name']]

# =============================================================================
# # Inventor-Patent-Table
# =============================================================================
invPatTable = pd.DataFrame()
invPatTable['inventor_id'] = inventorsTable['inventor_id']
invPatTable['patent_id'] = patentsTable['patent_id']
invPatTable['id'] = np.arange(1, len(invPatTable) + 1)
invPatTable = invPatTable[['id', 'inventor_id', 'patent_id']]

# =============================================================================
# # Assignee-Patent-Table
# =============================================================================
assPatTable = pd.DataFrame()
assPatTable['assignee_id'] = assigneesTable['assignee_id']
assPatTable['patent_id'] = patentsTable['patent_id']
assPatTable['id'] = np.arange(1, len(assPatTable) + 1)
assPatTable = assPatTable[['id', 'assignee_id', 'patent_id']]

# =============================================================================
# # Attorney-Patent-Table
# =============================================================================
attPatTable = pd.DataFrame()
attPatTable['attorney_id'] = attorneysTable['attorney_id']
attPatTable['patent_id'] = patentsTable['patent_id']
attPatTable['id'] = np.arange(1, len(attPatTable) + 1)
attPatTable = attPatTable[['id', 'attorney_id', 'patent_id']]

# Export the excel file
with pd.ExcelWriter(location + "\\sampleExport.xlsx") as writer:
	patentsTable.to_excel(writer, sheet_name = 'patents-table', index = False)
	inventorsTable.to_excel(writer, sheet_name = 'inventors-table', index = False)
	assigneesTable.to_excel(writer, sheet_name = 'assignees-table', index = False)
	attorneysTable.to_excel(writer, sheet_name = 'attorneys-table', index = False)
	invPatTable.to_excel(writer, sheet_name = 'inventor-patent-table', index = False)
	assPatTable.to_excel(writer, sheet_name = 'assignee-patent-table', index = False)
	attPatTable.to_excel(writer, sheet_name = 'attorney-patent-table', index = False)
	
