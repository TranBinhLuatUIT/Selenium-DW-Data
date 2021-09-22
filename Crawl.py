from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pyodbc
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver import ActionChains       
import random as r
import urllib.request
import os
from collections import defaultdict
from selenium.webdriver.chrome.options import Options
import json


#lấy tất cả hình ảnh của đồng hồ và lưu theo tên

def convert_color(text):
    dict_color = {'#e5ae87': 'rosegold', '#c1c1c1': 'silver', '#DFC96C': 'gold', '#00081C': 'black',
                  ' linear-gradient(145deg, #e5ae87 50%, #FFFFFF 50%)': 'satin-white',
                  ' linear-gradient(145deg, #c1c1c1 50%, #FFFFFF 50%)': 'satin-white',
                  ' linear-gradient(145deg, #e5ae87 50%, #00081C 50%)': 'black'}
    try:
        return dict_color[text]
    except:
        return 'none'
            
        
#lấy hình ảnh của sản phẩm trên trang 
def crawl_img(browser, product_name, color, size, folder):
    while(1):
        try:
            browser.find_element_by_xpath('//*[@id="maincontent"]/div/div/div[1]/div/div[1]/div').click()
            break
        except:
            browser.find_element_by_xpath('//*[@id="maincontent"]/div/div/div[1]/div/div[1]/div').click()
    sleep(r.randint(3, 5))
    slide_track = browser.find_element_by_class_name('slick-track')
    img = slide_track.find_elements_by_tag_name('img') 
    img = list(set([i.get_attribute('src') for i in img]))
    # name_xpath = '//*[@id="maincontent"]/section/div[2]/div[1]/h1'
    # name = browser.find_element_by_xpath(name_xpath).text
    # product_name = '_'.join(name.split(' ')).lower() 
    file_name = product_name + '_' + color + '_' + size
    product_folder = folder + product_name
    
    if (os.path.isdir(product_folder) == False):
        os.system('mkdir {}'.format(product_folder))
    
    for i in range(len(img)):
        urllib.request.urlretrieve(img[i], '{}\{}.png'.format(product_folder,file_name + '_' + str(i)))
    
    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
    sleep(2)


#lấy màu
def get_list_color_of_product(browser):
    main = browser.find_element_by_xpath('//*[@id="maincontent"]/section/div[3]/div/div/div/div[1]/div')
    color = main.find_elements_by_tag_name('span')
    color = [i.get_attribute('color') for i in color]
    color = list(map(lambda x: convert_color(x), color))
    
    return color
    

def get_list_size_of_product(browser):
    xpath_size = '//*[@id="maincontent"]/section/div[3]/div/div/div/div[2]/div/div[1]/div'
    size = browser.find_elements_by_tag_name('button')
    return [i.text for i in size]

#lấy từng thông tin về sản phẩm với màu và size hiện trên trang
def detail_product(browser, color, size):
    name = browser.find_element_by_xpath('//*[@id="maincontent"]/section/div[2]/div[1]/h1').text
    price = browser.find_element_by_xpath('//*[@id="maincontent"]/section/div[2]/div[2]/span').text
    infor = browser.find_element_by_xpath('//*[@id="gatsby-focus-wrapper"]/div/div[3]/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div[1]').text
    
    
    # size_details = {'size':, 'details': }

    detail = browser.find_element_by_xpath('//*[@id="gatsby-focus-wrapper"]/div/div[3]/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div[2]/div')
    detail = detail.find_elements_by_tag_name('span')
    detail = [i.text for i in detail]
    
    col = ['Price'] + [detail[i] for i in range(0,len(detail),2)]
    data = [price] + [detail[i+1] for i in range(0,len(detail),2)]
    
    detail = dict(zip(col,data))
    
    size_detail = {}
    size_detail[size] = detail
    
    color_dict = {}
    color_dict[color] = size_detail
    
    dict_data ={}
    dict_data['color'] = color_dict
    dict_data['color'][color]['information'] = infor
    
    dict_data_by_name = {}
    dict_data_by_name[name] = dict_data
    
    return dict_data_by_name


def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


#Lấy tất cả hình ảnh, thông tin của 1 sản phẩm size, màu, ...
def get_one_product(browser, folder):
    xpath_color = '//*[@id="maincontent"]/section/div[3]/div/div/div/div[1]/div'
    color_bar = browser.find_element_by_xpath(xpath_color)
    num_color = len(color_bar.find_elements_by_tag_name('button'))
    xpath_size = '//*[@id="maincontent"]/section/div[3]/div/div/div/div[2]/div/div[1]/div' #những sản phẩm khác
    # xpath_size = '//*[@id="maincontent"]/section/div[3]/div/div/div[3]/div[1]/div' #dành cho rings
    size_bar = browser.find_element_by_xpath(xpath_size)
    num_size = len(size_bar.find_elements_by_tag_name('button'))
    all_color_size_product = {}
    name_xpath = '//*[@id="maincontent"]/section/div[2]/div[1]/h1'
    name = browser.find_element_by_xpath(name_xpath).text
    product_name = '_'.join(name.split(' ')).lower() 
    product_folder = folder + product_name
    
    if (os.path.isdir(product_folder) == True):
        product_name += '-1'

    for i in range(1,num_color + 1):
        temp_color = xpath_color + '/button[' + str(i) + ']' 
        color_button = browser.find_element_by_xpath(temp_color)
        color = convert_color(color_button.find_element_by_tag_name('span').get_attribute('color'))
        color_button.click()
        sleep(3)
        
        for j in range(1,num_size + 1):
            temp_size = xpath_size + '/button[' + str(j) + ']'
            try:
                size = browser.find_element_by_xpath(temp_size)
                size_watch = size.text
                size.click()
            except:
                size = 'none'
            sleep(3)
            crawl_img(browser, product_name, color, size_watch, folder)
            temp_dict = detail_product(browser, color, size_watch)
            all_color_size_product = dict(mergedicts(all_color_size_product, temp_dict))
        

    return all_color_size_product


#lấy thông tin của từng product trong trang
def get_all_product_in_page(browser, folder, link, category):
    while(1):
        try:
            browser.get(link)
            break
        except: 
            browser.get(link)
    sleep(3)
    xpath = '//*[@id="maincontent"]/ul/li'
    list_pro = browser.find_elements_by_xpath(xpath)
    list_link_pro = [i.find_element_by_tag_name('a') for i in list_pro]
    list_link_pro = [i.get_attribute('href') for i in list_link_pro]
    dict_all_product = {}
    
    for url in list_link_pro:
        #mở tab
        browser.execute_script("window.open('');")
        browser.switch_to.window(browser.window_handles[1])
        while(1):
            try:
                browser.get(url)
                break
            except:
                browser.get(url)
            
        sleep(r.randint(1, 3))
        try:
            dict_a_product = get_one_product(browser, folder)
        except:
            continue
        
        for key, value in dict_a_product.items():
            if (key in dict_all_product.keys()):
                new_dict_a_product = {}
                new_key = key + '-1'
                new_dict_a_product[new_key] = dict_a_product[key]
                dict_all_product = dict(dict_all_product, **new_dict_a_product)
    
            else:
            
                dict_all_product = dict(dict_all_product, **dict_a_product)
        
        with open('products\{}.json'.format(category), 'w') as fp:
            json.dump(dict_all_product, fp)
        
        
        #đóng tab
        browser.close()
        sleep(r.randint(1, 3))
        
        browser.switch_to.window(browser.window_handles[0])
        sleep(2)

    return dict_all_product

