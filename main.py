from Crawl import *
browser = webdriver.Chrome(executable_path="./chromedriver")


dict_link = {
    "women-watches": 'https://www.danielwellington.com/us/womens-watches/',
    "men-watches": 'https://www.danielwellington.com/us/mens-watches/',
    'bracelets': 'https://www.danielwellington.com/us/earrings/'    
}

#rings phải xài xpath riêng

dict_all_product = {}

#key là loại sản phẩm, value là link của trang chính chứa sản phẩm
for key, value in dict_link.items():
    dict_product = get_all_product_in_page(browser, 'products', value, key)
    dict_all_product[key] = dict_product
    
with open('db.json', 'w') as fp:
    json.dump(dict_all_product, fp)