from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pyodbc
from selenium.common.exceptions import NoSuchElementException        
import random as r


MA_CP = 'SCG'

# 1. Khai báo browser
browser = webdriver.Chrome(executable_path="./chromedriver")

# 2. Mở URL của post
browser.get("https://www.stockbiz.vn/Stocks/{}/HistoricalQuotes.aspx".format(MA_CP))
sleep(5)
browser.find_element_by_xpath('/html/body/div[2]/div/div[1]/div/button').click()

#3. Thay đổi ngày
date_start = browser.find_element_by_id('ctl00_webPartManager_wp1770166562_wp1427611561_dtStartDate_picker_picker')
date_start.click()
date_start.clear()
date_start.send_keys('2000')
date_start.send_keys(Keys.ENTER)
browser.find_element_by_id('ctl00_webPartManager_wp1770166562_wp1427611561_btnView').click()


#4. crawl 1 ngày

def get_header():
    header = browser.find_elements_by_xpath('//*[@id="ctl00_webPartManager_wp1770166562_wp1427611561_callbackData"]/table/tbody/tr[1]/th')
    list_header = [i.text for i in header]
    list_header.pop(-1)
    return list_header

def get_data():
    num_row = len(browser.find_elements_by_xpath('//*[@id="ctl00_webPartManager_wp1770166562_wp1427611561_callbackData"]/table/tbody/tr')) 
    num_col = 9
    list_row_content=[]
    
    for row in range(2,num_row+1):
        row_cell = []
        for col in range(1,num_col+1):
            xpath = '//*[@id="ctl00_webPartManager_wp1770166562_wp1427611561_callbackData"]/table/tbody/tr[{}]/td[{}]'.format(row,col)
            cell = browser.find_elements_by_xpath(xpath)
            cell = [i.text for i in cell]
            row_cell.append(*cell)
        list_row_content.append(row_cell)
        
    return list_row_content

def get_all_data():
    def check_exists_by_xpath(xpath):
        try:
            browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
    
    list_row_content=get_data()
    
    for i in range(200):
        if(check_exists_by_xpath("//*[contains(text(), 'Tiếp »')]")==True):
            browser.find_element_by_xpath("//*[contains(text(), 'Tiếp »')]").click()
            sleep(r.randint(1, 5))
            list_row_content += get_data()
        else:
            break
    
    return list_row_content
        


#5. convert dataframe
list_all_content = get_all_data() 
list_header = get_header()
df = pd.DataFrame(data=list_all_content,columns=list_header)


#đóng browser 
browser.close()

df.to_csv('{}.csv'.format(MA_CP))